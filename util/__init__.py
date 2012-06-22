def has_matching(l, criteria):
    for i in l:
        if criteria(i):                                                                                                                                                                                          
            return True

    return False
