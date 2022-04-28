import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import matplotlib.transforms as transforms
import matplotlib.pyplot as plt
import matplotlib.lines as lines


# Generic formatting functions applied to all plots
def annotate_xrange(xmin, xmax,
                    label=None,
                    offset=-0.1,
                    width=-0.1,
                    ax=None,
                    patch_kwargs={'facecolor': 'yellow'},
                    line_kwargs={'color': 'black', 'linewidth':'1'},
                    text_kwargs={}
                    ):
    if ax is None:
        ax = plt.gca()

    # x-coordinates in axis coordinates,
    # y coordinates in data coordinates
    # trans = transforms.blended_transform_factory(
    #     ax.transAxes, ax.transData)

    # x-coordinates in data coordinates,
    # y coordinates in axis coordinates
    trans = transforms.blended_transform_factory(
        ax.transData, ax.transAxes)

    # a bar indicting the range of values
    rect = Rectangle((xmin, offset), height=width, width=xmax-xmin,
                     transform=trans, clip_on=False, **patch_kwargs)


    # delimiters at the start and end of the range mimicking ticks
    delimiter = Line2D((xmin, xmax), (offset, offset),
                           transform=trans, clip_on=False, **line_kwargs)
    # max_delimiter = Line2D((xmax, xmax), (offset+width, offset),
    #                        transform=trans, clip_on=False, **line_kwargs)
    ax.add_artist(delimiter)
    # ax.add_artist(max_delimiter)

    # label
    if label:
        x = xmin + 0.5 * (xmax - xmin)
        y = offset + 0.5 * width
        # we need to fix the alignment as otherwise our choice of x
        # and y leads to unexpected results;
        # e.g. 'right' does not align with the minimum_delimiter
        ax.text(x, y, label,
                horizontalalignment='center', verticalalignment='center',
                clip_on=False, transform=trans, **text_kwargs)

def hierarchical_axis(levels, width=-0.1, offsets=None):

    if not offsets:
        offsets = [x*-0.1 for x in range(1, len(levels)+1)]

    for ii, (level, offset, labels) in enumerate(zip(([level.values() for level in levels]), offsets, [list(level.keys()) for level in levels])):
        for jj, (xmin, xmax) in enumerate(level):
            annotate_xrange(
                xmin, xmax, labels[jj], offset=offset, width=width)

def make_grades_pretty(ax, task_order):

    tasks = pd.DataFrame(task_order.keys(), index=task_order.values()).reset_index().rename(columns={'index':'position', 0: 'year', 1:'task'})

    xlabels = [f'{y}' for x, y in task_order.keys()]
    plt.xticks(np.arange(0, np.max(list(task_order.values()))+1), labels=xlabels)

    level_1 = {
        str(year): (df['position'].min(), df['position'].max())
        for year, df in tasks.groupby('year')
    }

    level_2 = {'Assessment Task': (0, np.max(list(task_order.values())))}
    levels = [level_1, level_2]

    hierarchical_axis(levels)

    ax.set_ylim(0, 100)
    plt.ylabel('Overall score (%)')
    plt.tight_layout()


def make_wellbeing_class_pretty(ax, type_order, type_labels):

    ax.set_xlabel('')

    keys = pd.DataFrame(type_order.keys(), index=type_order.values()).reset_index().rename(columns={'index':'position', 0: 'year', 1:'type'})

    xlabels = [f'{x}' for x, y in type_order.keys()]
    plt.xticks(np.arange(0, np.max(list(type_order.values()))+1), labels=xlabels)


    level_2 = {
        type_labels[wb_type]: (df['position'].min(), df['position'].max())
        for wb_type, df in keys.groupby('type')
    }

    levels = [{}, level_2]

    hierarchical_axis(levels)

    handles, labels = ax.get_legend_handles_labels()
    labels = ['Term 1', 'Term 2', 'Term 3', 'Term 4']
    plt.legend(handles, labels, title='')

    plt.ylabel('Number of incidents')
    plt.tight_layout()

def make_wellbeing_student_pretty(ax, term_order, student):

    ax.set_xlabel('')

    keys = pd.DataFrame(term_order.keys(), index=term_order.values()).reset_index().rename(columns={'index':'position', 0: 'year', 1:'term'})

    xlabels = [f'{y}' for x, y in term_order.keys()]
    plt.xticks(np.arange(0, np.max(list(term_order.values()))+1), labels=xlabels)


    level_1 = {
        str(year): (df['position'].min(), df['position'].max())
        for year, df in keys.groupby('year')
    }


    level_2 = {'Term': (0, np.max(list(term_order.values())))}
    levels = [level_1, level_2]

    hierarchical_axis(levels)

    handles, labels = ax.get_legend_handles_labels()
    labels = ['Whole school', 'English negatives', 'English positives']
    plt.legend(handles, labels, title='Incident type', bbox_to_anchor=(1.0, 1.0))
    plt.title(student)

    plt.ylabel('Number of incidents')
    plt.tight_layout()

if __name__ == '__main__':

    fig, ax = plt.subplots(1, 1)
    fig.subplots_adjust(left=0.3)
    plt.xlim(-0.5, 11.5)
    make_grades_pretty(ax)
    plt.show()
