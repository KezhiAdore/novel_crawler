if [ ! -d "log" ]; then
        echo "创建log文件夹"
        mkdir "log"
fi

nohup python main.py --df_id 0 --start 0 --end 10000 >> log/run_0.log 2>&1 &
nohup python main.py --df_id 1 --start 10000 --end 20000 >> log/run_1.log 2>&1 &
nohup python main.py --df_id 2 --start 20000 --end 30000 >> log/run_2.log 2>&1 &
nohup python main.py --df_id 3 --start 30000 --end 40000 >> log/run_3.log 2>&1 &
nohup python main.py --df_id 4 --start 40000 --end 50000 >> log/run_4.log 2>&1 &
nohup python main.py --df_id 5 --start 50000 --end 60000 >> log/run_5.log 2>&1 &
nohup python main.py --df_id 6 --start 60000 --end 70000 >> log/run_6.log 2>&1 &
nohup python main.py --df_id 7 --start 70000 --end 80000 >> log/run_7.log 2>&1 &
nohup python main.py --df_id 8 --start 80000 --end 90000 >> log/run_8.log 2>&1 &
nohup python main.py --df_id 9 --start 90000 --end 100000 >> log/run_9.log 2>&1 &
nohup python main.py --df_id 10 --start 100000 --end 110000 >> log/run_10.log 2>&1 &
nohup python main.py --df_id 11 --start 110000 --end 120000 >> log/run_11.log 2>&1 &
nohup python main.py --df_id 12 --start 120000 --end 130000 >> log/run_12.log 2>&1 &