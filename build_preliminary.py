"""Build the instructor-feedback revision; run run_notebook.py afterward."""
from pathlib import Path
import importlib.metadata as meta
import json
import platform
import nbformat as nbf

root = Path(__file__).resolve().parent
manifest = json.loads((root/'hourly_manifest.json').read_text())
cells=[]
def md(text): cells.append(nbf.v4.new_markdown_cell(text))
def code(text): cells.append(nbf.v4.new_code_cell(text))

md("# Can a forecast help GMU decide when to salt?\nWe want to help the crew answer one question at **4 p.m. Eastern: should we salt before tonight, or wait?**\n\nWe predict the lowest Dulles air temperature recorded each hour from **6 p.m. to 8 a.m. the next morning**. We use only earlier nights to make the prediction. We do not use tonight's weather readings before they would be available.\n\nDulles air temperature is a stand-in for what happens on campus. It does not tell us directly whether a parking lot froze. Following the professor's feedback, we test three possible cutoffs:\n\n| Assumed margin below 32°F | Dulles temperature counted as a freeze warning |\n|---|---|\n| 2°F | 30°F or below |\n| 4°F | 28°F or below |\n| 6°F | 26°F or below |\n\nThese are **assumptions**, not measured campus-to-airport differences. We show all three instead of picking the one with the best test result. Pavement being colder than air does not, by itself, prove the direction or size of the difference between these two locations. We need readings from both places to check it.\n\nWe compare our forecast with **waiting to see ice**, as the professor requested. We also compare it with a simple forecast that repeats the previous night's temperature.\n\nThis version replaces the earlier analysis that used a whole-day minimum and a 32°F cutoff. Feedback: https://github.com/mrahma32/aii600-final-project/issues/1 .\n\n**AI use:** ChatGPT/Codex helped write the code and explanations. We are responsible for checking and understanding the work.\n")
code('''from pathlib import Path
import gzip
import hashlib
import io
import json
import zipfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.linear_model import LinearRegression
from IPython.display import display, Markdown

ROOT = Path.cwd()
FIG = ROOT / 'fig'
FIG.mkdir(exist_ok=True)
MARGINS = [2, 4, 6]
RATIOS = [2, 5, 10]
SEED = 600
rng = np.random.default_rng(SEED)
plt.rcParams.update({'figure.figsize': (10,4), 'axes.spines.top': False, 'axes.spines.right': False})
def save(name):
    plt.tight_layout()
    plt.savefig(FIG/name, dpi=150, bbox_inches='tight')
    plt.show()
''')
md("## Where the data comes from\nWe use NOAA's hourly weather records for **Dulles Airport, station 724030-93738 (KIAD)**. NOAA's station file confirms the name and location: latitude 38.935, longitude −77.447, elevation 89.5 metres. The source files and instructions are listed in `data/README.md`.\n\nThe records give air temperature in tenths of a degree Celsius. We convert it to Fahrenheit and change the time from UTC to Eastern, including daylight-saving changes. Early-morning readings belong to the night that started the previous evening.\n\nWe keep a night only when every expected hourly temperature is available. A normal night has 15 readings; nights when the clocks change have 14 or 16. We leave missing readings out rather than making up temperatures. Leaving out incomplete nights could still affect the results if missing data is more common in certain weather.\n\nNOAA selects readings near the hour and chooses between duplicates. This smaller dataset, called ISD-Lite, does not include the original quality flags or add more quality checks. We cannot confirm the quality of each reading. Also, the real low could occur between hourly readings.\n\nWe use nights starting in **2000–2024**. This archive stops partway through 2025, so 2024 is the last full year. The start of the 2025 file supplies the morning after December 31, 2024. We chose the end date because of data availability, not because it gave a better score.\n\nBefore reading the data, the code checks its SHA-256 hash—a file fingerprint—to confirm that we are using the same saved copy.\n")
code(f'''manifest = json.loads((ROOT/'hourly_manifest.json').read_text())
archive = ROOT/'data'/manifest['archive']
assert manifest['sha256'] == '{manifest['sha256']}'
assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['sha256'], 'Wrong hourly snapshot'
frames=[]
with zipfile.ZipFile(archive) as z:
    assert set(z.namelist()) == set(manifest['files'])
    for name, info in manifest['files'].items():
        data = z.read(name)
        assert hashlib.sha256(data).hexdigest() == info['sha256'], name
        if name.endswith('.gz'):
            part = pd.read_csv(io.BytesIO(gzip.decompress(data)), sep=r'\\s+', header=None,
                               usecols=[0,1,2,3,4], names=['year','month','day','hour','temp_tenths_c'])
            frames.append(part)
    history = pd.read_csv(io.BytesIO(z.read('isd-history.csv')), dtype=str)
station = history[(history.USAF == '724030') & (history.WBAN == '93738')]
assert len(station) == 1 and station.iloc[0].ICAO == 'KIAD'
display(station)
raw = pd.concat(frames, ignore_index=True)
times = pd.to_datetime(raw[['year','month','day','hour']], utc=True)
assert not times.duplicated().any(), 'Duplicate source timestamps need review'
values = raw.temp_tenths_c.where(raw.temp_tenths_c != -9999) / 10 * 9/5 + 32
hourly = pd.Series(values.to_numpy(), index=pd.DatetimeIndex(times), name='air_f').sort_index()
# Construct the expected grid independently of observed records; preserve missing slots.
grid = pd.date_range('2000-01-01', '2025-01-02', freq='h', tz='UTC').tz_convert('America/New_York')
h = hourly.reindex(grid).to_frame()
local = h.index.tz_localize(None)
h['night_date'] = local.normalize() - pd.to_timedelta((local.hour <= 8).astype(int), unit='D')
h = h[(h.index.hour >= 18) | (h.index.hour <= 8)]
night = h.groupby('night_date').agg(tmin_f=('air_f','min'), observed_hours=('air_f','count'), expected_hours=('air_f','size'))
night = night.reindex(pd.date_range('2000-01-01','2024-12-31',name='night_date'))
night.loc[night.observed_hours != night.expected_hours, 'tmin_f'] = np.nan
print('Hourly source records:', len(raw))
print('Candidate nights:', len(night), '; complete nights:', night.tmin_f.notna().sum(), '; excluded incomplete nights:', night.tmin_f.isna().sum())
display(night.expected_hours.value_counts().sort_index().rename('candidate_nights').to_frame())
display(night[['tmin_f']].describe().round(2))
ax=night.tmin_f.plot(lw=.45, alpha=.7, color='#176b87')
for margin, color in zip(MARGINS, ['#c47d18','#a33030','#702e8c']):
    ax.axhline(32-margin, ls='--', lw=1, color=color, label=f'Assumed margin {{margin}}°F → cutoff {{32-margin}}°F')
ax.set(title='Observed Dulles hourly-sampled overnight minima, 18:00–08:00 Eastern', ylabel='Airport air temperature (°F)', xlabel='Evening decision date')
ax.legend(fontsize=8, ncol=1)
save('raw_temperature.png')
''')
md("## How we split the data and make predictions\nWe use three separate time periods:\n\n| Years | Purpose |\n|---|---|\n| 2000–2018 | Train the model: learn the relationship between earlier temperatures and tonight's low. |\n| 2019–2021 | Estimate uncertainty: use forecast errors to build a range of possible temperatures. This step is called calibration. |\n| 2022–2024 | Test: score predictions on later nights that were not used in either step above. |\n\nLater years make a more realistic test than mixing years randomly. We do not use test results to choose model settings, margins, or cost ratios. We had already looked at the earlier daily-temperature test before making this feedback revision, so we do not claim this was a plan written before seeing any results.\n\nAt 4 p.m., the previous night has already ended at 8 a.m. We use that night and the night before it, plus the time of year. We do not fill gaps or treat an older available record as 'yesterday.' We still need to check whether these archived readings would have been published in time for a real 4 p.m. decision.\n\n**Simple comparison forecast:** tonight's low equals the previous night's low. This is often called persistence.\n\n**Our model:** a linear regression combines the two earlier nights with a seasonal pattern:\n\n$T_t=\\beta_0+\\beta_1T_{t-1}+\\beta_2T_{t-2}+\\beta_3\\sin(2\\pi d_t/365.2425)+\\beta_4\\cos(2\\pi d_t/365.2425)+e_t$.\n\nHere $T_t$ is tonight's low; the two earlier $T$ values are past lows; $d_t$ is the day of the year; and $e_t$ is the prediction error. The intercept $\\beta_0$ shifts the forecast in °F. The lag coefficients say how the forecast changes with each earlier temperature, holding the other inputs fixed. The sine and cosine terms describe the yearly temperature cycle in °F. These are patterns in the data, not proof of cause and effect.\n\nA more complex model might handle sudden weather changes better. We start with this model because we can explain it clearly. Its weakest assumption is that past temperature patterns and forecast errors still apply to future cold weather.\n\nFor each method, we add its 2019–2021 errors to the predicted temperature to get possible outcomes: $T_t^*=\\hat T_t+e_j^{cal}$. The 5th and 95th percentiles give a range intended to contain 90% of future lows. This range is not guaranteed to work equally well in every season.\n")
code('''df=night[['tmin_f']].copy()
df['lag1']=df.tmin_f.shift(1)
df['lag2']=df.tmin_f.shift(2)
angle=2*np.pi*(df.index.day_of_year-1)/365.2425
df['sin_year'],df['cos_year']=np.sin(angle),np.cos(angle)
features=['lag1','lag2','sin_year','cos_year']
usable=df.dropna(subset=['tmin_f']+features)
train=usable.loc[:'2018-12-31'].copy()
cal=usable.loc['2019-01-01':'2021-12-31'].copy()
test=usable.loc['2022-01-01':'2024-12-31'].copy()
assert train.index.max() < cal.index.min() < test.index.min()
# The most recent predictor night ends at 08:00, eight hours before the 16:00 decision.
assert (test.index + pd.Timedelta(hours=8) < test.index + pd.Timedelta(hours=16)).all()
split_table=pd.DataFrame([{'split':name,'first_evening':str(p.index.min().date()),'last_evening':str(p.index.max().date()),'nights':len(p),
    **{f'proxy_freeze_m{m}':int((p.tmin_f<=32-m).sum()) for m in MARGINS}}
    for name,p in [('train',train),('calibration',cal),('test',test)]])
display(split_table)
print('Excluded target/predictor rows:', len(df)-len(usable))
model=LinearRegression().fit(train[features],train.tmin_f)
display(pd.Series([model.intercept_,*model.coef_],index=['intercept']+features,name='coefficient').round(4).to_frame())
pred_cal={'Persistence':cal.lag1.to_numpy(),'Forecast rule':model.predict(cal[features])}
pred_test={'Persistence':test.lag1.to_numpy(),'Forecast rule':model.predict(test[features])}
errors_cal={name:cal.tmin_f.to_numpy()-p for name,p in pred_cal.items()}
actual=test.tmin_f.to_numpy()
intervals={}
forecast_rows=[]
prob={}
for name,pred in pred_test.items():
    err=errors_cal[name]
    lo,hi=np.quantile(err,[.05,.95])
    intervals[name]=(pred+lo,pred+hi)
    forecast_rows.append({'method':name,'MAE_F':abs(actual-pred).mean(),'RMSE_F':np.sqrt(np.mean((actual-pred)**2)),
        'mean_error_F':(actual-pred).mean(),'90pct_interval_coverage':((actual>=pred+lo)&(actual<=pred+hi)).mean(),'interval_width_F':hi-lo})
    for margin in MARGINS:
        prob[name,margin]=(pred[:,None]+err[None,:] <= 32-margin).mean(axis=1)
forecast_scores=pd.DataFrame(forecast_rows)
display(forecast_scores.round(4))
forecast_scores.to_csv(FIG/'forecast_scores.csv',index=False)
split_table.to_csv(FIG/'split_summary.csv',index=False)
''')
md("## When should the crew send the trucks?\nFor each assumed margin $m$, a warning means the Dulles overnight low is at or below $32-m$°F. The model estimates the chance of crossing that cutoff:\n\n$p=P(T_{night}\\le32-m\\mid\\text{earlier observations})$.\n\nThis is a chance of an **airport-temperature warning**, not a checked probability of ice on a campus lot.\n\nWe count two mistakes:\n\n- **A missed night:** the warning cutoff is crossed, but we did not salt beforehand.\n- **Salted for nothing:** we salt, but the warning cutoff is not crossed.\n\nLet $C_m$ be the cost of a missed night and $C_w$ the cost of salting unnecessarily. Our score is:\n\n$L=C_m\\times\\text{missed nights}+C_w\\times\\text{nights salted for nothing}$.\n\nWe do not know GMU's dollar costs. We therefore count one unnecessary salting night as **one penalty unit** and try missed-night costs of **2, 5, and 10 units**. A penalty unit is a comparison score, not a dollar.\n\nIf the predicted chance is $p$, sending trucks has expected cost $C_w(1-p)$, and waiting has expected cost $C_mp$. Send trucks when the first is lower:\n\n**Salt when $p>C_w/(C_m+C_w)$.**\n\n| Missed-night cost / unnecessary-salting cost | Salt when the predicted chance is above |\n|---|---|\n| 2 to 1 | 33.33% |\n| 5 to 1 | 16.67% |\n| 10 to 1 | 9.09% |\n\nAt exactly the threshold, both actions have the same expected cost. Our code waits at that tie.\n\n**Required baseline: wait to see ice.** Following the professor's example, this rule misses the night the ice first forms. In our scoring, it misses every warning night and has no unnecessary preventive salting. The crew could react later; this does not mean they never salt. We did not observe GMU's actual actions or measure the harm from responding late.\n\nWe score every rule on the **same test nights**, using the **same cutoff and costs**. Repeating the previous night's temperature is an extra comparison. Salting every night is another reference.\n\nThis simple score gives zero penalty for correct decisions. It leaves out wetness, incomplete salt effectiveness, environmental effects, and the costs of salting correctly. It is not a full operating budget or a final policy recommendation.\n")
code('''decision_rows=[]
nightly_predictions=pd.DataFrame({'decision_date':test.index,'overnight_min_F':actual})
for margin in MARGINS:
    freeze=actual<=32-margin
    for name in pred_test:
        nightly_predictions[f'{name}_p_margin_{margin}']=prob[name,margin]
    for ratio in RATIOS:
        threshold=1/(ratio+1)
        methods={'Wait to see ice':np.zeros(len(test),dtype=bool),
                 'Forecast rule':prob['Forecast rule',margin]>threshold,
                 'Persistence':prob['Persistence',margin]>threshold,
                 'Always salt':np.ones(len(test),dtype=bool)}
        for name,action in methods.items():
            missed=int((~action & freeze).sum())
            wasted=int((action & ~freeze).sum())
            total=ratio*missed+wasted
            decision_rows.append({'margin_F':margin,'Dulles_cutoff_F':32-margin,'Cm_over_Cw':ratio,'method':name,
                'probability_threshold':threshold,'test_nights':len(test),'proxy_freeze_nights':int(freeze.sum()),
                'salted_nights':int(action.sum()),'missed_nights':missed,'salted_for_nothing_nights':wasted,
                'total_penalty_units':total,'penalty_per_100_nights':100*total/len(test)})
scores=pd.DataFrame(decision_rows)
# Check baseline interpretation, scoring, and monotonicity of the action across assumed costs/margins.
wait=scores[scores.method=='Wait to see ice']
assert (wait.missed_nights==wait.proxy_freeze_nights).all() and (wait.salted_for_nothing_nights==0).all()
assert (scores.total_penalty_units == scores.Cm_over_Cw*scores.missed_nights+scores.salted_for_nothing_nights).all()
for name in pred_test:
    assert np.all(prob[name,2] >= prob[name,4]) and np.all(prob[name,4] >= prob[name,6])
    for margin in MARGINS:
        counts=[(prob[name,margin]>1/(r+1)).sum() for r in RATIOS]
        assert counts==sorted(counts)
primary=scores[scores.method.isin(['Wait to see ice','Forecast rule'])]
display(primary[['margin_F','Dulles_cutoff_F','Cm_over_Cw','method','missed_nights','salted_for_nothing_nights','total_penalty_units']])
scores.to_csv(FIG/'decision_scores.csv',index=False)
nightly_predictions.to_csv(ROOT/'data/nightly_predictions.csv',index=False)
fig,axes=plt.subplots(1,3,figsize=(14,4),sharey=True)
for ax,margin in zip(axes,MARGINS):
    sub=scores[(scores.margin_F==margin)&scores.method.isin(['Wait to see ice','Forecast rule'])]
    sub.pivot(index='Cm_over_Cw',columns='method',values='penalty_per_100_nights')[['Wait to see ice','Forecast rule']].plot.bar(ax=ax,rot=0,color=['#777777','#176b87'])
    ax.set(title=f'Assumed margin {margin}°F: cutoff {32-margin}°F',xlabel='Missed-night cost / wasted-salt cost')
    ax.get_legend().remove()
axes[0].set_ylabel('Penalty units per 100 held-out nights')
axes[-1].legend(fontsize=8)
fig.suptitle('Afternoon forecast vs waiting for ice — same 18:00–08:00 held-out nights',y=1.03)
save('decision_loss.png')
# Show the two actual scoring components for every scenario, without hiding them in a weighted total.
fig,axes=plt.subplots(2,3,figsize=(14,7),sharey='row')
for j,margin in enumerate(MARGINS):
    for i,(col,title) in enumerate([('missed_nights','Nights missed'),('salted_for_nothing_nights','Nights salted for nothing')]):
        sub=primary[primary.margin_F==margin]
        sub.pivot(index='Cm_over_Cw',columns='method',values=col)[['Wait to see ice','Forecast rule']].plot.bar(ax=axes[i,j],rot=0,color=['#777777','#176b87'])
        axes[i,j].set(title=f'{title}; margin {margin}°F',xlabel='Cost ratio Cm/Cw')
        axes[i,j].get_legend().remove()
axes[0,0].set_ylabel('Held-out nights'); axes[1,0].set_ylabel('Held-out nights')
axes[0,-1].legend(fontsize=8)
fig.suptitle('A forecast can avoid missed nights at the cost of unnecessary salting',y=1.02)
save('missed_and_wasted_nights.png')
# Thresholds are determined by costs, independently of the temperature-margin assumption.
p_grid=np.linspace(0,1,1001)
fig,ax=plt.subplots(figsize=(10,4))
ax.plot(p_grid,1-p_grid,color='black',lw=2,label='Send trucks: Cw × (1−p), Cw=1')
for ratio,color in zip(RATIOS,['#3b8c6e','#c47d18','#702e8c']):
    ax.plot(p_grid,ratio*p_grid,color=color,label=f'Stand down: Cm × p, Cm={ratio}')
    ax.axvline(1/(ratio+1),ls='--',color=color,alpha=.6)
ax.set(xlim=(0,.55),ylim=(0,2),xlabel='Predicted proxy-freeze probability p',ylabel='Expected penalty units',title='Dispatch when p exceeds Cw / (Cm + Cw)')
ax.legend(fontsize=8,ncol=2)
save('cost_thresholds.png')
# Chronological example: first 60 test-season decision nights (not chosen for the largest improvement).
winter=test.index[(test.index.month>=11)|(test.index.month<=3)][:60]
fig,axes=plt.subplots(3,1,figsize=(11,8),sharex=True)
mask=test.index.isin(winter)
for ax,margin in zip(axes,MARGINS):
    ax.plot(test.index[mask],prob['Forecast rule',margin][mask],label='Forecast proxy-freeze probability',color='#176b87')
    for ratio,color in zip(RATIOS,['#3b8c6e','#c47d18','#702e8c']):
        ax.axhline(1/(ratio+1),ls='--',color=color,label=f'Cm/Cw={ratio}: {1/(ratio+1):.1%}')
    events=(actual<=32-margin)&mask
    ax.scatter(test.index[events],np.full(events.sum(),.98),marker='v',color='black',s=20,label='Observed proxy-freeze night')
    ax.set(ylim=(-.03,1.04),ylabel='Probability',title=f'Assumed margin {margin}°F: cutoff {32-margin}°F')
axes[-1].xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
axes[-1].set_xlabel('Evening decision date (first 60 winter test nights)')
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(.5,-.04), ncol=3, fontsize=8)
save('nightly_probability.png')
''')
md('## How reliable are the predictions?\nFor each assumed margin, we group predictions into five fixed probability ranges and compare the predicted chance with how often the airport warning actually happened. For example, predictions near 20% should lead to warnings about 20% of the time. This check is called **calibration**. It does not check whether campus pavement actually froze.\n\nWe also look at **residuals**, meaning actual temperature minus predicted temperature. A positive error means the forecast was too cold; a negative error means it was too warm. We check whether errors change over time, with temperature, or by season.\n\nThese are checks on the finished model. We do not use the test results to refit it. We only tested this one overnight forecast window, so we cannot say how it works several nights ahead.\n')
code('''residual=actual-pred_test['Forecast rule']
fig,axes=plt.subplots(1,3,figsize=(14,4),sharex=True,sharey=True)
calibration_rows=[]
for ax,margin in zip(axes,MARGINS):
    outcome=actual<=32-margin
    for name in pred_test:
        p=prob[name,margin]
        group=pd.DataFrame({'bin':pd.cut(p,np.linspace(0,1,6),include_lowest=True),'p':p,'event':outcome}).groupby('bin',observed=True)
        table=group.agg(mean_probability=('p','mean'),observed_fraction=('event','mean'),nights=('event','size'))
        ax.plot(table.mean_probability,table.observed_fraction,'o-',label=name)
        table['method'],table['margin_F']=name,margin
        calibration_rows.append(table.reset_index())
    ax.plot([0,1],[0,1],'--',color='gray')
    ax.set(title=f'Margin {margin}°F / cutoff {32-margin}°F',xlabel='Predicted proxy-freeze probability')
axes[0].set_ylabel('Observed proxy-freeze fraction')
axes[-1].legend(fontsize=8)
save('residuals_calibration.png')
calibration_table=pd.concat(calibration_rows,ignore_index=True)
display(calibration_table.round(3))
calibration_table.to_csv(FIG/'calibration_scores.csv',index=False)
fig,axes=plt.subplots(1,2,figsize=(11,4))
axes[0].scatter(test.index,residual,s=5,alpha=.4)
axes[0].axhline(0,color='black',lw=1)
axes[0].xaxis.set_major_locator(mdates.YearLocator())
axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
axes[0].set(title='Test residuals through time',ylabel='Actual − predicted overnight minimum (°F)')
axes[1].scatter(pred_test['Forecast rule'],residual,s=5,alpha=.4)
axes[1].axhline(0,color='black',lw=1)
axes[1].set(xlabel='Predicted overnight minimum (°F)',title='Errors against predicted temperature')
save('temperature_residuals.png')
lo,hi=intervals['Forecast rule']
seasonal=pd.DataFrame({'season':np.where(test.index.month.isin([11,12,1,2,3]),'Nov–Mar','Apr–Oct'),
    'covered':(actual>=lo)&(actual<=hi),'residual_F':residual}).groupby('season').agg(nights=('covered','size'),coverage=('covered','mean'),mean_error_F=('residual_F','mean'))
display(seasonal.round(4))
yearly=pd.DataFrame({'year':test.index.year,'error_F':residual,'abs_error_F':abs(residual)}).groupby('year').agg(nights=('error_F','size'),mean_error_F=('error_F','mean'),MAE_F=('abs_error_F','mean'))
display(yearly.round(3))
autocorr=pd.Series(residual,index=test.index).reindex(df.index).autocorr()
print('Lag-1 test residual correlation (calendar gaps preserved):',round(autocorr,3))
comparison=primary.pivot(index=['margin_F','Cm_over_Cw'],columns='method',values='total_penalty_units')
comparison['saving_vs_waiting']=comparison['Wait to see ice']-comparison['Forecast rule']
display(comparison)
summary={'test_nights':len(test),'complete_nights':int(night.tmin_f.notna().sum()),'candidate_nights':len(night),
    'train_nights':len(train),'calibration_nights':len(cal),'excluded_model_rows':len(df)-len(usable),
    'forecast_MAE_F':float(forecast_scores.loc[1,'MAE_F']),'persistence_MAE_F':float(forecast_scores.loc[0,'MAE_F']),
    'interval_coverage':float(forecast_scores.loc[1,'90pct_interval_coverage']),
    'cold_season_coverage':float(seasonal.loc['Nov–Mar','coverage']),'residual_lag1':float(autocorr)}
(FIG/'result_summary.json').write_text(json.dumps(summary,indent=2)+'\\n')
display(Markdown(f"**What the numbers mean:** our forecast is off by {summary['forecast_MAE_F']:.2f}°F on average. Repeating the previous night's low is off by {summary['persistence_MAE_F']:.2f}°F. The range meant to cover 90% of nights actually covers {summary['interval_coverage']:.1%} overall and only {summary['cold_season_coverage']:.1%} in November–March. That cold-weather gap is a weakness. The correlation between errors on neighboring nights is {autocorr:.3f}; the error plots help show whether mistakes follow a pattern. The table above compares all nine assumptions without picking a favorite from the test results. A perfect forecast would score zero in this simple system, so the current penalty is the most it could save here—not a promise of actual savings."))
''')
md('## Does the fitting code work on a known example?\nWe create artificial temperatures using known model weights and random errors. We then fit the regression and compare its estimated weights with the ones we put in. We use random seed 600 so the example can be repeated.\n\nThis checks whether the code can recover known values. It does not prove that real weather follows the same assumptions. The plot compares errors from this artificial example with errors from the real training data.\n')
code('''X=train[features].to_numpy()
beta=np.array([8.,.6,.2,3.,-4.])
sim_y=beta[0]+X@beta[1:]+rng.normal(0,6,len(train))
sim_fit=LinearRegression().fit(X,sim_y)
display(pd.DataFrame({'parameter':['intercept']+features,'generating':beta,'recovered':[sim_fit.intercept_,*sim_fit.coef_]}).round(3))
plt.hist(train.tmin_f-model.predict(train[features]),bins=45,density=True,alpha=.6,label='Real training residuals')
plt.hist(sim_y-sim_fit.predict(X),bins=45,density=True,alpha=.5,label='Simulated residuals')
plt.xlabel('Residual (°F)'); plt.ylabel('Density'); plt.legend()
save('simulation_check.png')
''')
md("## What the results can and cannot tell us\nThe steps are: **past weather → possible temperatures tonight → chance of crossing an assumed cutoff → salt or wait based on the two costs**.\n\nThe margin and the costs do different jobs. The margin changes which airport temperature counts as a warning. The costs change how much warning probability is enough to send trucks. Making a missed freeze more expensive does not change the weather itself.\n\nOur main limits are:\n\n- We followed the professor's below-32°F rule, but we have no paired campus-pavement and airport readings to check the direction or size of that difference. We therefore show several assumed margins.\n- Air temperature alone does not tell us whether a lot is wet or icy, or whether salt would work. We did not measure injuries or real dollar savings.\n- Hourly readings can miss a colder temperature between readings. The source also lacks the original quality flags. Leaving out incomplete nights may affect which conditions we test.\n- These are archived records. Later corrections or reporting delays could make a real-time forecast different.\n- The model's prediction ranges work less well during cold weather. We should not treat good overall results as proof that the model is ready for use.\n\nWe already saw the earlier daily-temperature test before correcting the analysis. We made these changes to follow the professor's feedback, not to search for whichever model looks best on the test data. Before the final presentation, we should check the margin with local readings, discuss realistic costs, and confirm what data the crew could actually have at 4 p.m.\n")
code('''fig,ax=plt.subplots(figsize=(14,2.5))
ax.axis('off')
labels=['Completed earlier nights\\nNOAA hourly air data','Temperature model\\n+ calibration errors','P(Tnight ≤ 32−m)\\nassumed m=2,4,6°F','Send trucks if p >\\nCw/(Cm+Cw)']
for i,label in enumerate(labels):
    x=.12+i*.25
    ax.text(x,.5,label,ha='center',va='center',fontsize=9,bbox={'boxstyle':'round,pad=.6','facecolor':'#e5f2f5','edgecolor':'#176b87'},transform=ax.transAxes)
    if i<3:
        ax.annotate('',xy=(x+.15,.5),xytext=(x+.105,.5),xycoords='axes fraction',arrowprops={'arrowstyle':'->'})
save('layers.png')
''')
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3 (project .venv)','language':'python','name':'python3'}})
nbf.write(nb,root/'analysis.ipynb')
(root/'.python-version').write_text(platform.python_version()+'\n')
packages=['numpy','pandas','matplotlib','scikit-learn','ipython','nbformat','nbclient','ipykernel','tzdata']
(root/'requirements.txt').write_text('\n'.join(f'{p}=={meta.version(p)}' for p in packages)+'\n')
print('Built revised notebook:',sum(c.cell_type=='code' for c in cells),'code cells')
