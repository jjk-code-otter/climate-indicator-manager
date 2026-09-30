import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from climind.config.config import DATA_DIR

STANDARD_PARAMETER_SET = {
    'axes.axisbelow': False,
    'axes.labelsize': 23,
    'xtick.labelsize': 23,
    'ytick.labelsize': 23,
    'axes.edgecolor': 'dimgrey',
    'axes.facecolor': 'None',

    'axes.grid.axis': 'y',
    'grid.color': 'lightgrey',
    'grid.alpha': 0.5,

    'axes.labelcolor': 'dimgrey',
    'axes.labelpad': 4,

    'axes.spines.left': False,
    'axes.spines.right': False,
    'axes.spines.top': False,

    'figure.facecolor': 'white',
    'lines.solid_capstyle': 'round',
    'patch.edgecolor': 'w',
    'patch.force_edgecolor': True,
    'text.color': 'dimgrey',

    'xtick.bottom': True,
    'xtick.color': 'dimgrey',
    'xtick.direction': 'out',
    'xtick.top': False,
    'xtick.labelbottom': True,

    'ytick.major.width': 0.4,
    'ytick.color': 'dimgrey',
    'ytick.direction': 'out',
    'ytick.left': False,
    'ytick.right': False
}


data = [
    [1991, -0.6649117308179122, -1.6448741472513768, 2.0281089226728137, -0.4983986802698947],
    [1992, -1.2156822961526732, -0.9704646952040397, 0.21211830842598145, -1.935459463967679],
    [1993, -0.6967057734524499, 0.05080385053568252, 5.063357572811, -0.4659696245046671],
    [1994, -0.008235368615705787, 0.5498689284547446, 1.7166051093493653, -2.3084726432947997],
    [1995, -0.2240680544953565, -0.4218332251321827, 5.067953824932952, -0.9767315248276798],
    [1996, 0.17098065731432507, 0.1541659581152846, 5.441459016968232, 1.3432921060720173],
    [1997, -0.1779498891086032, -0.2823976283841009, 3.013392758150471, -1.9305180881349278],
    [1998, -0.5365534523450832, -0.6675035595627413, 8.802011004462234, 0.46314388206390933],
    [1999, 0.06462051389016828, 0.24756030153264938, 3.0495241057331937, -3.7727383749439256],
    [2000, -0.06515739394351644, -0.13418966204266453, 1.4424804115648393, -1.3393623734122584],
    [2001, 0.19528722856995676, -0.34049274714247707, -2.6311073313124904, -1.8609239340163801],
    [2002, 0.6995972774767834, 0.8432288658198005, -0.1835888900348147, -1.8700233835700377],
    [2003, 0.5402066911881188, -0.29558971612655627, -2.7895792079629733, 1.0811939992223807],
    [2004, 0.11642097473270269, 0.11646844036229172, -2.903570164030131, -2.1734792556416913],
    [2005, 0.4538982270973693, -1.2771822903227499, -2.6579397982049375, 2.572803079260781],
    [2006, 0.11489053559684952, -1.3670566978688992, -4.4545455088628065, -0.7668618813027198],
    [2007, 0.5224392631233713, 0.8888916906210708, -2.787418415304687, -2.1449308167684134],
    [2008, 0.4193383530904849, 0.7064000137204016, -1.4999166186575608, -1.3957227728679187],
    [2009, 0.4393557880332487, -1.1933529156207827, -5.276762294864344, 1.1146970750543788],
    [2010, -0.4394638297263411, -0.13493577603009654, 3.233559590106122, 6.058161683149875],
    [2011, 0.213266867267184, 0.008518688694769726, -4.996234317736177, 1.025401885044262],
    [2012, 0.47829668690161276, -0.553635620404226, -2.6160918733749985, 3.51904975303206],
    [2013, 0.06132253434811314, 0.6397493255765632, -1.2840882795466984, 1.07366096670467],
    [2014, 0.1044618452272887, 0.335704869897956, -1.9346987920101644, -0.9520234793302802],
    [2015, -0.0503648956031794, 1.6546948845874998, -2.0148950566470725, -0.17291010382862024],
    [2016, -0.7151817762534709, -1.4807326608735285, 2.40231650109771, 2.82466890325661],
    [2017, -0.057338516012439576, 1.5255851162392138, -1.3333258668896835, 1.047010248659742],
    [2018, 0.09177676762239058, 0.1917597809463855, -2.2177014957452417, 1.8077817429535534],
    [2019, 0.0806464620518597, 0.3947655250062935, -2.537149398357834, 1.5655585472976872],
    [2020, 0.08480630299470092, 2.456075101855909, 2.6457261832675267, -0.9318974710898325],
    [2021, 0.4960389481521634, 1.3324573299149878, -2.240431901972751, 0.32163369624040666],
    [2022, 0.5258020639682179, 1.7963775510900135, -3.6125224759662333, 1.5215099400915297],
    [2023, 0.9003605932807476, -0.3780189975853704, -5.226352439966563, -0.12715284155982298],
    [2024, 0.033391427442912194, 1.0205398760775142, 1.617601600359949, 4.103354773175097],
    [2025, 0.26507941603907703, 0.028871112748170977, -1.9995662473957376, 0.4112327855159274]
]


data = np.array(data)

wmo_cols = ['#543005', '#bf812d', '#e5e5e5', '#35978f', '#003c30']

sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)
plt.figure(figsize=[16, 9])

plt.plot(data[:, 0], data[:, 1], linewidth=4, color="#F4A528")
plt.plot(data[:, 0], data[:, 2], linewidth=4, color="#23AAD1")
plt.plot(data[:, 0], data[:, 3], linewidth=4, color="#214F96")
plt.plot(data[:, 0], data[:, 4], linewidth=4, color="#A2CD41")

ntime = data.shape[0]

plt.tick_params(
    axis='y',  # changes apply to the x-axis
    which='both',  # both major and minor ticks are affected
    left=False,  # ticks along the bottom edge are off
    right=False,  # ticks along the top edge are off
    labelright=False)

sns.despine(right=True, top=True, left=True)
plt.gca().set_ylim(-7, 10)
plt.gca().set_xlim(1990, 2026)
plt.yticks([-6., -4, -2, 0, 2, 4, 6, 8, 10])
plt.xticks([1995,2000,2005,2010,2015,2020,2025])

ylim = plt.gca().get_ylim()
yloc = ylim[1] + 0.035 * (ylim[1] - ylim[0])

plt.text(plt.gca().get_xlim()[0], yloc, "Global average as percentage change from 1991-2020 average", fontdict={'fontsize': 30})
plt.gca().set_title("Renewable energy generation and demand proxies", pad=55,
                    fontdict={'fontsize': 40}, loc='left')

plt.text(2026,0.5, "Solar Power CF", fontdict={'fontsize': 30}, color="#F4A528")
plt.text(2026,-0.5, "Wind Power CF", fontdict={'fontsize': 30}, color="#23AAD1")
plt.text(2026,-2.2, "Hydro Power proxy", fontdict={'fontsize': 30}, color="#214F96")
plt.text(2026,2., "Energy demand proxy", fontdict={'fontsize': 30}, color="#A2CD41")

project_dir = DATA_DIR / "ManagedData"
figure_dir = project_dir / 'Figures'
image_filename = 'renewables.png'

plt.savefig(figure_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [16.5, 10]]))
plt.savefig(figure_dir / image_filename.replace('png', 'pdf'))
plt.savefig(figure_dir / image_filename.replace('png', 'svg'))
plt.close('all')
