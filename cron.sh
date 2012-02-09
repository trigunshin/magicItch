#!/bin/bash
DEVDIR="/home/pcrane/dev/"
PYDEVDIR=$DEVDIR"python/"
ITCHDIR=$PYDEVDIR"magicItch/"
SRCDIR=$ITCHDIR"src/"
INFODIR=$ITCHDIR"info/"
DAILYDIR=$ITCHDIR"daily/"
HOMEDIR="/home/pcrane/"
LOGDIR=$HOMEDIR"logs/"
DATE=$(date -I)
YEST=$(date -I -d '1 day ago')

python $SRCDIR"magicTraders.py" -f $INFODIR >> $LOGDIR"log"$DATE".log" \
    && python $SRCDIR"mongoExport.py" -f $INFODIR -d $DATE -n "mtgtrdr_"$DATE".tsv" -s "Magic Traders" >>$LOGDIR"log"$DATE".log" \
    && python $SRCDIR"mongoPriceReport.py" -s $YEST -e $DATE -o $DAILYDIR -c -n mtgtrdrDaily$DATE".txt" -r "Magic Traders" >>$LOGDIR"log"$DATE".log" \
    && python $SRCDIR"mongoPriceReport.py" -s $YEST -e $DATE -o $DAILYDIR -n mtgtrdrDaily$DATE".csv" -r "Magic Traders" >>$LOGDIR"log"$DATE".log"
python $ITCHDIR"allinMain.py" -f $INFODIR >>$LOGDIR"log"$DATE".log" \
    && python $SRCDIR"mongoExport.py" -f $INFODIR -d $DATE >>$LOGDIR"log"$DATE".log" \
    && python $SRCDIR"mongoPriceReport.py" -s $YEST -e $DATE -o $DAILYDIR -c -n scgDaily$DATE".txt" >>$LOGDIR"log"$DATE".log" \
    && python $SRCDIR"mongoPriceReport.py" -s $YEST -e $DATE -o $DAILYDIR -n scgDaily$DATE".csv" >>$LOGDIR"log"$DATE".log"
python $SRCDIR"sendMuxGmail.py" -d $DAILYDIR >>$LOGDIR"log"$DATE".log"
#python $SRCDIR"sendGmail.py" -f $DAILYDIR"scgDaily"$DATE".txt" -f $DAILYDIR"mtgtrdrDaily"$DATE".txt" >>$LOGDIR"log"$DATE".log"
