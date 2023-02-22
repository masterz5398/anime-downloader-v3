import os


def eRX(Err):
    pass


def unDuplicate(lst):
    return list(set(lst))


def commands(command="c"):
    if command == "c":
        os.system("cls")


def Int(val, Err=None):
    try:
        return int(val)
    except Exception as e:
        eRX(e)
        if Err is not None:
            return Err
        else:
            return val


def check_sum(lst, vrb: str or list):
    if type(vrb) == str:
        vrbX = 0
        for i in lst:
            if i in vrb:
                vrbX += 1
        return (vrbX / len(lst)) * 100
    elif type(vrb) == list:
        dicX = {key: 0 for key in vrb}
        for i in vrb:
            for j in lst:
                if j in i:
                    dicX[i] += 1
        x = list(dicX.values())
        x.sort()
        sorted_vrb = []
        for iX in range(len(x)):
            for i in vrb:
                if dicX[i] == x[iX]:
                    sorted_vrb.append(i)
        lx = {key: (dicX[key] / len(lst)) * 100 for key in sorted_vrb}
        ml = []
        for i in sorted_vrb:
            same = []
            for j in sorted_vrb:
                if lx[i] == lx[j]:
                    same.append(i)
            if same not in ml:
                ml.append(same)
        return [sorted_vrb, lx, ml]
    else:
        print(type(vrb).value, "not supported")


def check_one(lst, vrb: True or False or list or str or int):
    try:
        tr = False
        for i in lst:
            try:
                if i in vrb:
                    tr = True
            except Exception as e:
                eRX(e)
                if i is vrb:
                    tr = True
        return tr
    except Exception as e:
        eRX(e)
        return None


def check(lst, vrb: list or str or int):
    tr = True
    for i in lst:
        try:
            if i not in vrb:
                tr = False
        except Exception as e:
            eRX(e)
            if i is not vrb:
                tr = False
    return tr


def reverse_str(strX):
    return strX[::-1]


def optionsX(options, values, int_ing=False, replace_while_printing=None, query="", print_all=True, print_only=""):
    if replace_while_printing is None:
        replace_while_printing = ["", ""]
    if query != "":
        print(query)
    if True:
        vX = True
        vY = True
        for option in options:
            if Int(option, Err="ERX") == "ERX":
                # print("NOT all Options are not ints...")
                vX = False
                break
        else:
            for value in values:
                if Int(value, Err="ERX") == "ERX":
                    # print("NOT all Values are not ints...")
                    vY = False
                    break
        # if vX:
        #     print("Options are all ints")
        # if vY:
        #     print("Values are all ints")
        # if check([vY, vX], True):
        #     int_ing = True
        # else:
        #     int_ing = False
        if vY:
            int_ing_val = True
        else:
            int_ing_val = False
        if vX:
            int_ing_opt = True
        else:
            int_ing_opt = False
    inX = check_one([int_ing, int_ing_val, int_ing_opt], True)
    # print(inX)
    if len(options) != len(values):
        print("error: options and values do not match")
        for option in options:
            type_prev = options[0]
        return None
    else:
        opt_dic = {}
        val_dic = {}
        if print_all:
            for i in range(len(options)):
                print(str(options[i]).replace(replace_while_printing[0], replace_while_printing[1]), "->",
                      str(values[i]).replace(replace_while_printing[0], replace_while_printing[1]))
                if inX:
                    # print(Int(i))
                    opt_dic[Int(options[i])] = i
                else:
                    opt_dic[options[i]] = i
                if inX:
                    val_dic[Int(i)] = values[i]
                else:
                    val_dic[i] = values[i]
        elif print_all is False:
            for i in range(len(options)):
                if inX:
                    # print(Int(i))
                    opt_dic[Int(options[i])] = i
                else:
                    opt_dic[options[i]] = i
                if inX:
                    val_dic[Int(i)] = values[i]
                else:
                    val_dic[i] = values[i]
            if type(print_only) == list:
                for i in range(len(print_only[0])):
                    print(str(print_only[0][i]).replace(replace_while_printing[0], replace_while_printing[1]), "->",
                          str(print_only[1][i]).replace(replace_while_printing[0], replace_while_printing[1]))
            elif type(print_only) == str:
                if print_only != "":
                    print(print_only)
            elif type(print_only) == dict:
                print_only: dict
                for i in list(print_only.keys()):
                    print(i.replace(replace_while_printing[0], replace_while_printing[1]), "->", str(print_only[i]).
                          replace(replace_while_printing[0], replace_while_printing[1]))
    i = input("select your choice: ")
    options = [Int(i) for i in options]
    if inX:
        i = Int(i)
    while i not in options:
        print("option invalid")
        i = input("select your choice: ")
        if inX:
            i = Int(i)
    else:
        # print(opt_dic)
        # print(val_dic)
        # print(type(i))
        # print(i)
        try:
            value = val_dic[opt_dic[i]]
        except KeyError:
            value = val_dic[opt_dic[Int(i)]]
        commands()
        print("you selected", value)
        if int_ing:
            return Int(value)
        else:
            return str(value)


def multi_choice(options, values, int_ing=False, replace_while_printing=None, query="", print_all=True, print_only=""):
    i = "yes"
    selected = []
    while i == "yes":
        selected.append(optionsX(options, values, int_ing, replace_while_printing, query, print_all, print_only))
        i = optionsX(["y", "n"], ["yes", "no"], query="do you want to select another value")
        commands()
    return selected


def dict_2_list(dictionary):
    ks = [key for key in dictionary]
    vs = [dictionary[key] for key in dictionary]
    return [ks, vs]


def to_list(string, sort=False, unDup=True):
    lst = [char for char in string]
    if sort:
        lst.sort()
    if unDup:
        return unDuplicate(lst)
    else:
        return lst


def merge(lst1, lst2):
    if type(lst1) == type(lst2):
        if type(lst1) == list:
            for i in lst2:
                lst1.append(i)
            return lst1
        elif type(lst1) == dict:
            for k, v in lst1.items():
                if isinstance(v, dict):
                    merge(v, lst2.setdefault(k, {}))
                else:
                    if k not in lst2:
                        lst2[k] = v
            return lst2

# TODO: check sum fix
# optionsX(["y", "n"], ["yes", "no"], query="do you want to continue downloading?")
# print(check_sum(to_list("kawtec"), to_list("check", False)))
# diX = {"1": "nex", "2": "awd"}
# print(multi_choice(dict_2_list(diX)[0], dict_2_list(diX)[1], query="choice test:"))
# print(type(optionsX([1234, 2324, 2425], [245, "2we", "23re awz"], True)))
# print(multi_choice([1234, 2324, 2425], [245, "2we", "23re-awz"]))
