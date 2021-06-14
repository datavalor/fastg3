def format_number(n):
    if n>1000000:
        return '{:.1f}'.format(n/1000000)+"M"
    elif n>100000:
        return '{:.0f}'.format(n/1000)+"K"
    else:
        return '{:.1f}'.format(n/1000)+"K"