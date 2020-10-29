from src.client import OutputCustomer,Reader,Base
from multiprocessing import Queue,Process
from threading import Thread
from server.start import start_web
import multiprocessing,time,sys,os





def runReader(log_files_conf):

    r = Reader(log_file_conf=log_files_conf)

    jobs = ['readLog', 'cutFile']
    t = []
    for i in jobs:
        th = Thread(target=r.runMethod, args=(i,))
        t.append(th)

    for i in t:
        i.start()

    for i in t:
        i.join()


def customer():
    obj = OutputCustomer()
    getattr(obj, obj.call_engine)()

def getLogFilsDict(conf):
    logFiles = []

    for i in list(conf):
        if 'client.log_file' in i:
            item = dict(base.conf[i])
            item['app_name'] = i.split('.')[-1]
            logFiles.append(item)

    return logFiles

if __name__ == "__main__":

    base = Base()

    args = sys.argv[1:]
    if args[0] == '-run' :
        if args[1] == 'client':

            logFiles = getLogFilsDict(base.conf)

            plist = []
            for i in logFiles:
                p = Process(target=runReader, args=( i, ))
                plist.append(p)


            for i in plist:
                i.start()

            for i in plist:
                i.join()

        elif args[1] == 'customer':

            p_list = []
            for i in range( int(base.conf['custom']['worker_process_num']) ):
                p = Process(target = customer)
                p_list.append(p)

            for i in p_list:
                i.start()

            for i in p_list:
                i.join()

        elif args[1] == 'web':
            web_conf = dict(base.conf['web'])
            web_conf[ web_conf['data_engine'] ] = dict(base.conf[ web_conf['data_engine'] ])

            # web_p = Process(target=start_web, args=(web_conf,))
            # web_p.start()
            # web_p.join()

            start_web(web_conf)


        else:
            raise ValueError('example: python3 startClient.py -run [client | customer]')

    elif args[0] == '-stop':
        if args[1] not in ['client' ,'customer']:
            raise ValueError('-stop only support [client | customer]')


        res = os.popen('ps -ax | grep "run.py -run %s"' % args[1])
        pids = []
        print('|============================================================')
        for i in res.readlines():
            if i.find('grep') != -1:
                continue
            print('| %s ' % i.strip())
            pids.append(i.strip().split(' ')[0])


        if len(pids) == 0:
            print('| %s is not running ' % args[1])
            print('|============================================================')
            exit('nothing happened . bye bye !')


        print('|============================================================')

        confirm = input('confirm: please enter [ yes | y ] or [ no | n ]  : ')

        if confirm in ['yes','y'] and len(pids) > 0:

            os.popen('kill %s' % ' '.join(pids))
            exit('pid: %s was killed and %s is stoped. bye bye !' % (' '.join(pids) ,args[1]) )
        else:
            exit('nothing happened . bye bye !')

    else:
        raise ValueError('example: python3 run.py -run [client | customer]')