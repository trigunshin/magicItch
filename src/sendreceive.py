import sys,os,traceback
from datetime import date

from emailer import send_email
from sprites import outsideIn
from processSprites import processSprites
from mongoExport import spliceSpriteData
from mongoPriceReport import priceReport

from pymongo import MongoClient
from functools import partial
from kombu import Connection, Exchange, Queue
from kombu.common import maybe_declare
from kombu.mixins import ConsumerMixin
from kombu.pools import producers
from kombu.utils import kwdict, reprcall

rabbitURL = os.getenv("RABBIT_HOST","localhost")
connection_string = "amqp://bigdata:a@"+rabbitURL+":5672//"

priority_to_routing_key = {'itch': 'itch'}
task_exchange = Exchange('itch_tasks', type='direct')
task_queues = [Queue('itch', task_exchange, routing_key='itch')]

def hello_task(**varargs):
    for k,v in varargs.iteritems():
        print '\t',k,"||",v

def send_as_task(connection, fun, args=(), kwargs={}, priority='itch'):
    payload = {'fun': fun, 'args': args, 'kwargs': kwargs}
    routing_key = priority_to_routing_key[priority]
    with producers[connection].acquire(block=True) as producer:
        maybe_declare(task_exchange, producer.channel)
        producer.publish(payload,serializer='pickle',compression='bzip2',routing_key=routing_key)

def run_producer(conn,taskMap,command=None):
    print "Sending task..."
    if command is None: return send_as_task(conn, fun=hello_task.__name__, args=[], kwargs={'who':'Kombu'}, priority='itch') 
    
    try:
        taskMap[command]
        send_as_task(conn, fun=command, args=[],kwargs={},priority='itch')
        #send_as_task(conn, fun='hello_test', args=[], kwargs={}, priority='itch')
        #send_as_task(conn, fun='process_sprites', args=[], kwargs={}, priority='itch')
        #send_as_task(conn, fun='run_report', args=[], kwargs={'startDate':'2013-03-05'}, priority='itch')
        #send_as_task(conn, fun='run_report_error', args=[], kwargs={'startDate':'2013-03-05','err':'someError'}, priority='itch')
    except KeyError,e:
        print "Command",command,"not found. Exitting..."
    

class Worker(ConsumerMixin):
    def __init__(self, connection, taskmap=None):
        self.connection = connection
        if taskmap is None: self.taskMap = {'hello_task':hello_task}
        else: self.taskMap = taskmap
    
    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=task_queues,callbacks=[self.process_task])]
    
    def process_task(self, body, message):
        fun = self.taskMap[body['fun']]
        args = body['args']
        kwargs = body['kwargs']
        print 'Got task:', body['fun']#, args, kwargs
        try:
            result = fun(*args, **kwdict(kwargs))
            if result:
                print 'Result:'#print fun.__name__,result
                for k,v in result.iteritems():
                    print "\t",k,'||',v
        except Exception, exc:
            #re-queue the request
            #send_as_task(self.connection,body['fun'],args,kwargs,priority='itch')
            print "err", 'task raised exception:', exc
        message.ack()

def run_consumer(conn, taskMap=None):
    print "Awaiting tasks...\n"
    try:
        Worker(conn,taskMap).run()
    except KeyboardInterrupt:
        print('done')

def wrapCall(conn, func, success_msg, err_msg):
    def newfunc(*fargs, **fkeywords):
        try:
            ret = func(*fargs, **fkeywords)
            if ret is None: ret = {}
            #fire successMsg
            send_as_task(conn,success_msg,[],ret,priority='itch')
            return ret
        except Exception,e:
            print e
            #fire rabbit w/errMsg
            argd={'err':str(e),'trace':traceback.format_exc()}
            send_as_task(conn,err_msg,[],argd,priority='itch')
            raise e
    newfunc.func = func
    return newfunc

def auto_alert_handler(processName, **varargs):
    send_email("MagicItch Error:"+processName,'\n'.join([`k`+'||'+`v` for k,v in varargs.iteritems()]))

if __name__ == "__main__":
    #daemon needs to know, for itch:
    """
    job names|HARDCODE
    store_data_dir
    daily_dir
    sprite_dir
    log_dir
    email PW, via $EMAIL_PASS
    mongo host, via $MONGO_HOST
    mongo port
    rabbit host, via $RABBIT_HOST
    db name
    spritecoll name
    carddatacoll name
    """
    
    rabbitURL = os.getenv("RABBIT_HOST","localhost")
    connection_string = "amqp://bigdata:a@"+rabbitURL+":5672//"
    priority_to_routing_key = {'itch': 'itch'}
    task_exchange = Exchange('itch_tasks', type='direct')
    task_queues = [Queue('itch', task_exchange, routing_key='itch')]
    
    mongoURL = os.getenv("MONGO_HOST","localhost")
    mongoPort = 27017
    dbName = "cardData"
    spriteCollName = "sprites"
    cardDataCollName = "priceCollection"
    reportDataCollName = "reports"
    
    HOMEDIR="/home/pcrane/"
    DEVDIR=HOMEDIR+"dev/"
    ITCHDIR=DEVDIR+"magicItch/"
    SRCDIR=ITCHDIR+"src/"
    SCG_DATA_DIR=ITCHDIR+"scg_data/"
    DAILY_REPORT_DIR=ITCHDIR+"daily/"
    SPRITE_DIR=ITCHDIR+"sprites/"
    LOGDIR=HOMEDIR+"logs/magicItch/"
    SPRITE_MAP_FILE=SRCDIR+"ocr_map.csv"
    DELIMITER = '\t'
    
    debug_flag=False
    verbose_flag=False
    
    mCli=MongoClient(mongoURL,mongoPort)
    db=mCli[dbName]
    spriteColl=db[spriteCollName]
    cardDataColl=db[cardDataCollName]
    reportDataColl=db[reportDataCollName]
    
    try:
        print "AMQP Connecting to ",connection_string,"..."
        conn = Connection(connection_string)
        print "...connected."
        
        hello_wrapped = wrapCall(conn, hello_task, "hello_task_success","hello_task_error")
        manual_email = partial(send_email, "Manual Test Email","Manual test stuffs")
        
        scgDownload = partial(outsideIn,spriteColl,fullFileDirectory=SCG_DATA_DIR,mappingFilePath=SPRITE_MAP_FILE,spriteFilePath=SPRITE_DIR,delimiter=DELIMITER,verbose=verbose_flag,debug=debug_flag)
        scgDownload = wrapCall(conn, scgDownload, 'scg_download_success','scg_download_error')
        scgDownload_error = partial(auto_alert_handler, 'scgDownload')
        
        spriteProcess = partial(processSprites,spriteColl,spriteDir=SPRITE_DIR,verbose=verbose_flag,debug=debug_flag)
        spriteProcess_wrapped = wrapCall(conn, spriteProcess, 'process_sprites_success','process_sprites_error')
        spriteProcess_error = partial(auto_alert_handler, 'spriteProcess')
        
        dataGenerate = partial(spliceSpriteData,spriteColl,cardDataColl,dataDirectory=SCG_DATA_DIR,datestring=None,storeName="StarCity Games", delimiter=DELIMITER,verbose=verbose_flag,debug=debug_flag)
        dataGenerate_wrapped = wrapCall(conn, dataGenerate, 'process_data_success','process_data_error')
        dataGenerate_error = partial(auto_alert_handler, 'dataGenerate')
        
        reportArgs={'startDate':None,'endDate':None,'outputDir':DAILY_REPORT_DIR,'quantityFilterFlag':False,'storeName':"StarCity Games",'storeShort':"scg",'humanFormat':True,'verbose':verbose_flag,'debug':debug_flag}
        runPriceReport = partial(priceReport,cardDataColl,reportDataColl,**reportArgs)
        runPriceReport_wrapped = wrapCall(conn, runPriceReport, 'run_report_success','run_report_error')
        reportGenerate_error = partial(auto_alert_handler, 'reportGenerate')
        #reportGenerate_success = #handle emailing the report here via dbmux or something easier for now
        
        #TODO tie in mailer w/reportgen, & use the rabbit_param for it
        #def send_email(subject="Test Email", extra_body_text='',attach=None,report_file_path=None,**kwargs):
        reportEmail = partial(send_email,subject="Report Generated Email",extra_body_text="Report successfully run, should be attached.",attach=None)
        report_email_wrapped = wrapCall(conn, reportEmail, 'report_email_success','report_email_error')
        
        taskMap = {
          'hello_task':hello_task,
          'hello_task_success':hello_task,
          'hello_task_error':hello_task,
          'hello_test':hello_wrapped,
          
          'scg_download_manual':scgDownload,
          'process_sprites_manual':spriteProcess,
          'process_data_manual':dataGenerate,
          'run_report_manual':runPriceReport,
          'send_email_manual':manual_email,
          
          #AMQP flow
          'scg_download':scgDownload,
          'scg_download_success':spriteProcess_wrapped,
          'scg_download_error':scgDownload_error,
          
          'process_sprites':spriteProcess_wrapped,
          'process_sprites_success':dataGenerate_wrapped,
          'process_sprites_error':spriteProcess_error,
          
          'process_data':dataGenerate_wrapped,
          'process_data_success':runPriceReport_wrapped,
          'process_data_error':dataGenerate_error,
          
          'run_report':runPriceReport_wrapped,
          'run_report_success':report_email_wrapped,
          'run_report_error':reportGenerate_error,
          
          'report_email':report_email_wrapped,
          'report_email_success':hello_task,
          'report_email_error':hello_task
        }
        #"""
        if sys.argv[0].startswith("python"):
            option_index = 2
        else:
            option_index = 1
        option = sys.argv[option_index]
        if option == "produce":
            try:command = sys.argv[option_index+1]
            except IndexError:command=None
            run_producer(conn,taskMap,command)
        elif option == "consume":
            run_consumer(conn,taskMap)
        else:
            print "Unknown option '%s'; exiting ..." % option
            sys.exit(1)
    finally: conn.close()
    #"""
