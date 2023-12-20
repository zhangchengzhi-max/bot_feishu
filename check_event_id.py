
def check(event_id):
    f = open('event_id.txt', 'r+')
    for i in f.readlines():
        i = i.strip()
        if str(event_id) == str(i):
            return False
            # return False
    f.close()



if __name__ == '__main__':
    print(check('9619e5ae2bfac1d419344beabe56bfa0'))