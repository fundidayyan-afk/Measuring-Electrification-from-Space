"""Map of the DHS regions used in the analysis (outputs/figures/study_regions.png)."""
import geopandas as gpd, matplotlib.pyplot as plt, pandas as pd
from config import ROOT, OUT_FIGURES
B=ROOT/'data'/'boundaries'
use={'Kenya 2022 (47 counties)':'KE2022DHS_sdr_subnational_boundaries','Tanzania 2022 (31 regions)':'TZ2022DHS_sdr_subnational_boundaries2',
     'Uganda 2016 (15 sub-regions)':'UG2016DHS_sdr_subnational_boundaries','Rwanda 2019-20 (5 provinces)':'RW2019DHS_sdr_subnational_boundaries','DR Congo 2023-24 (26 provinces)':'CD2023DHS_sdr_subnational_boundaries'}
cols=['#2a6f97','#c05746','#6a994e','#bc6c25','#7b5ea7']
fig,ax=plt.subplots(figsize=(9,7))
for (lab,f),c in zip(use.items(),cols):
    g=gpd.read_file(B/f'{f}.geojson'); g.plot(ax=ax,facecolor=c,edgecolor='white',linewidth=0.5,alpha=0.85,label=lab)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=c,label=l) for l,c in zip(use,cols)],loc='lower left',frameon=False,fontsize=9)
ax.set_title('DHS survey regions used in the analysis',loc='left',fontsize=12); ax.set_axis_off()
fig.savefig(OUT_FIGURES/'study_regions.png',dpi=150,bbox_inches='tight'); print('ok')
