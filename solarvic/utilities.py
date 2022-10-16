import numpy as np
import matplotlib.pyplot as plt


def pp(outputs, title='', numformat='{:.2f}'):
    """
    Write tables to output
    """
    if title:
        print(title)
    print('\t', '\t'.join(numformat.format(o) for o in outputs))
    return None


def print_table(table):
    """
    Wrapper around pp function
    """
    for idx in range(len(table)):
        pp(table[idx, :])
    return None


def print_consumption(consumption):
    """
    Wrapper around print_table function
    """
    for dt in consumption:
        print(dt)
        print_table(consumption[dt])
    return None


def plot(out, xl, yl, ti, outfile=''):
    """
    Plot typical day power output
    """
    plt.figure()
    plt.plot(out)
    plt.xlabel(xl)
    plt.ylabel(yl)
    plt.xticks(np.arange(24))
    plt.legend(np.arange(12) + 1)
    plt.title(ti)
    plt.grid(visible=True, axis='y')
    if outfile:
        plt.savefig(outfile)
    else:
        plt.show()
    return None
