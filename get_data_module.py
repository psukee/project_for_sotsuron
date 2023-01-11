# JEPX2018-2021年度までのファイルをまとめて返す関数 
# spotはシステムプライスと約定量
# intraday は　平均価格と取引量
# これに価格差とTimeの列を加えた6つの列を追加
def Get_JEPX():

    # JEPX 
    # spotはシステムプライスと約定量
    # intraday は　平均価格と取引量
    # これに価格差とTimeの列を加えた6つの列を追加

    # 全年分のJEPX用の用の空のデータフレーム
    df_jepx_total = pd.DataFrame(columns=['DateTime','intra_price(円/kWh)','spot_price(円/kWh)','gap_price[intra-spot](円/kWh)','intra_volume（MWh/h）','spot_volume(kWh)'])

    for year in range(2018,2023):

    # year = 2021
            
        df_spot=pd.read_csv(f'../../卒論関連書類/データ/JEPX_data/spot_{year}.csv',encoding='Shift-JIS')
        df_intraday = pd.read_csv(f'../../卒論関連書類/データ/JEPX_data/im_trade_summary_{year}.csv',encoding='Shift-JIS')

        # 一年分のjepx用の空のデータフレーム
        df_jepx  = pd.DataFrame(columns=['DateTime','intra_price(円/kWh)','spot_price(円/kWh)','gap_price[intra-spot](円/kWh)','intra_volume（MWh/h）','spot_volume(kWh)'])
        # //日付をTimeStamp型で追加
        date_list=[]

        spot_dates = df_spot['年月日'].values
        # 時刻コードを時間に直す(0時0分ー23時30分)
        time_code =df_spot['時刻コード'].values
        time_code = (time_code-1)*30
        hour_list,min_list = time_code//60, time_code%60
        for i in range(len(spot_dates)):
            str_date = f'{spot_dates[i]}/{hour_list[i]}/{min_list[i]}'
            date = dt.datetime.strptime(str_date,'%Y/%m/%d/%H/%M')
            date_list.append(date)
        df_jepx['DateTime'] = date_list
        # //
        # 他のデータを代入
        df_jepx['spot_price(円/kWh)'] = df_spot['システムプライス(円/kWh)']
        df_jepx['intra_price(円/kWh)'] = df_intraday['平均（円/kWh）']
        df_jepx['gap_price[intra-spot](円/kWh)'] = df_intraday['平均（円/kWh）']-df_spot['システムプライス(円/kWh)']
        df_jepx['intra_volume（MWh/h）'] = df_intraday['約定量合計（MWh/h）']
        df_jepx['spot_volume(kWh)'] = df_spot['約定総量(kWh)']

        # 一年分を全体に合算
        df_jepx_total = pd.concat([df_jepx_total,df_jepx],axis=0)
    df_jepx_total = df_jepx_total.reset_index(drop=True)
    return(df_jepx_total)



# 九州電力の想定値と実績地を返す関数
# 12月8日4:00の風力想定値のみ欠損
def Get_Kyuden_Plan():
    
    df_kyuden_total = pd.DataFrame(columns=['DateTime','九電太陽想定値(kWh)','九電太陽実績値(kWh)','九電風力想定値(kWh)','九電風力実績値(kWh)'])

    # 1-3が画翌年
    # 単位はkWh
    month_list =['4-6','7-9','10-12','1-3']
    sheet_name_list = ['太陽光想定','太陽光実績','風力想定','風力実績']
    col_names =np.array(list(range(49)),dtype='str')


    for year in range(2018,2023):
        if year==2022:
            month_list=month_list[:2]
        else:
            pass


        for month in month_list:
            for name_s in sheet_name_list[:]:

                df_read = pd.read_excel(f'../../卒論関連書類/データ/発電予測値/九州電力/td_{year}_{month}.xls',sheet_name=name_s,names=col_names)[3:]
                            # シート読み込みの初回にDatetime を作成する
                if name_s==sheet_name_list[0]:
                        # 一区切り分のデータをまとめるデータフレームの作成  
                    df = pd.DataFrame(columns=['DateTime','九電太陽想定値(kWh)','九電太陽実績値(kWh)','九電風力想定値(kWh)','九電風力実績値(kWh)'])

                    # ///読み取ったシートからTimeStampを制作する
                    # 日付の抽出
                    # Dates = df_read['0'].values
                    # 時刻のリストを作る
                    Times = np.array(list(range(0,48)))*30
                    hours,mins = Times//60,Times%60

                    datetime_list = []
                    #日付と時刻を合わせたリストを作る
                    for date in df_read['0']:
                        for i in range(48):

                            str_datetime = f'{date.year}/{date.month}/{date.day}/{hours[i]}/{mins[i]}'
                            datetime_list.append(dt.datetime.strptime(str_datetime,'%Y/%m/%d/%H/%M'))
                    # ///
                    df['DateTime'] = datetime_list
                else:
                    pass

                # ここから上はシートの読み込み一回のみ一度のみの処理
                # ここから下はシートの数繰り返し
                values_list =[]
                for num in range(len(df_read)):
                    values = df_read[num:num+1].values[0][1:]
                    values_list.extend(values)
                if name_s=='太陽光想定':
                    df['九電太陽想定値(kWh)']=values_list
                elif name_s=='太陽光実績':
                    df['九電太陽実績値(kWh)']=values_list
                elif name_s=='風力想定':
                    df['九電風力想定値(kWh)']=values_list
                elif name_s == '風力実績':
                    df['九電風力実績値(kWh)']=values_list
                else:
                    print('エラー九電')
            
            df_kyuden_total = pd.concat([df_kyuden_total,df],axis=0)

    df_kyuden_total = df_kyuden_total.reset_index(drop=True)
    return(df_kyuden_total)


# 東電の想定値と実績地を返す関数
def Get_Toden_Plan():

    df_toden_plan_king = pd.DataFrame(columns=['DateTime','東電太陽光想定(kWh)','東電太陽光実績(kWh)','東電風力想定(kWh)','東電風力実績(kWh)'])

    for year in range(2018,2023):
        df_toden_plan = pd.read_csv(f'../../卒論関連書類/データ/発電予測値/東京電力/fit-{year}.csv',encoding='shift-jis')
        df_toden_plan_total = pd.DataFrame(columns=['DateTime','東電太陽光想定(kWh)','東電太陽光実績(kWh)','東電風力想定(kWh)','東電風力実績(kWh)'])

        # timestampの列を作成
        date_list =  df_toden_plan['DATE'].values
        time_list = df_toden_plan['TIME'].values
        str_datetime_list = date_list+'/'+time_list

        datetime_list = []
        for str_datetime in str_datetime_list:
            datetime = dt.datetime.strptime(str_datetime,'%Y/%m/%d/%H:%M')
            datetime_list.append(datetime)
        # 値の代入
        df_toden_plan_total['DateTime'] = datetime_list
        df_toden_plan_total['東電太陽光想定(kWh)'] = df_toden_plan['太陽光想定(kWh)']
        df_toden_plan_total['東電太陽光実績(kWh)'] = df_toden_plan['太陽光実績(kWh)']
        df_toden_plan_total['東電風力想定(kWh)'] = df_toden_plan['風力想定(kWh)']
        df_toden_plan_total['東電風力実績(kWh)'] = df_toden_plan['風力実績(kWh)']

        # 結合
        df_toden_plan_king = pd.concat([df_toden_plan_king,df_toden_plan_total],axis=0)
    df_toden_plan_king = df_toden_plan_king.reset_index(drop=True)
    return(df_toden_plan_king)

# 関電の想定値と実績地を返す関数
def Get_Kanden_Plan():

    df_kanden_plan_king = pd.DataFrame(columns=['DateTime','関電太陽光想定(kWh)','関電太陽光実績(kWh)','関電風力想定(kWh)','関電風力実績(kWh)'])

    for year in range(2018,2023):
        df_kanden_plan =pd.read_csv(f'../../卒論関連書類/データ/発電予測値/関西電力/{year}fit1_soutei_jisseki.csv',encoding='shift-jis')
        df_kanden_plan_total = pd.DataFrame(columns=['DateTime','関電太陽光想定(kWh)','関電太陽光実績(kWh)','関電風力想定(kWh)','関電風力実績(kWh)'])

        str_datetime_list = df_kanden_plan['DATE_TIME'].values
        datetime_list=[]
        for str_datetime in str_datetime_list:
            datetime = dt.datetime.strptime(str_datetime,'%Y/%m/%d %H:%M')
            datetime_list.append(datetime)
        # 値の代入
        df_kanden_plan_total['DateTime'] = datetime_list
        df_kanden_plan_total['関電太陽光想定(kWh)'] = df_kanden_plan['FIT1_太陽光想定値［kWh］']
        df_kanden_plan_total['関電太陽光実績(kWh)'] = df_kanden_plan['FIT1_太陽光実績値［kWh］']
        df_kanden_plan_total['関電風力想定(kWh)'] = df_kanden_plan['FIT1_風力想定値［kWh］']
        df_kanden_plan_total['関電風力実績(kWh)'] = df_kanden_plan['FIT1_風力実績値［kWh］']

        # 結合
        df_kanden_plan_king = pd.concat([df_kanden_plan_king,df_kanden_plan_total],axis=0)
    df_kanden_plan_king = df_kanden_plan_king.reset_index(drop=True)
    return(df_kanden_plan_king)


#中国電力の想定値と実績値を返す関数
 
def Get_Chugoku_Plan():
    columns = ['DATE','TIME','中国太陽光想定(kWh)','中国風力想定(kWh)','中国太陽光実績(kWh)','中国風力実績(kWh)']
    # ファイルを全て読み込み
    df_chugoku_plan_2020_ = pd.read_csv('../../卒論関連書類/データ/発電予測値/中国電力/fit_tokurei1.csv',encoding='shift-jis',names=columns)[3:]
    df_chugoku_plan_2018 = pd.read_csv('../../卒論関連書類/データ/発電予測値/中国電力/kako-2018.csv',encoding='shift-jis',names=columns)[3:].dropna()
    df_chugoku_plan_2019 = pd.read_csv('../../卒論関連書類/データ/発電予測値/中国電力/kako-2019.csv',encoding='shift-jis',names=columns)[3:].dropna()
    # データを結合
    df_total_chugoku_plan =pd.concat([df_chugoku_plan_2018,df_chugoku_plan_2019,df_chugoku_plan_2020_],axis=0).reset_index(drop=True)
    # //timestampを作成
    datetime_list = []
    date_list, time_list = df_total_chugoku_plan['DATE'].values, df_total_chugoku_plan['TIME'].values

    for i in range(len(date_list)):
        str_datetime = date_list[i]+'/'+time_list[i]
        datetime_list.append(dt.datetime.strptime(str_datetime,'%Y/%m/%d/%H:%M'))
    # //
    df_total_chugoku_plan['DateTime'] = datetime_list
    df_total_chugoku_plan = df_total_chugoku_plan.drop(columns=['DATE','TIME'])
    # 左側にDateTimeを持ってきた
    df_total_chugoku_plan =df_total_chugoku_plan.reindex(columns=['DateTime','中国太陽光想定(kWh)','中国風力想定(kWh)','中国太陽光実績(kWh)','中国風力実績(kWh)']) 
    return(df_total_chugoku_plan)


def Get_yobiritu():
    # 広域予備率はエリアごとでまとめる
    # 沖縄だけは省く
    df_yobiritu = pd.read_csv('../../卒論関連書類/データ/広域予備率/yobiritsu.csv')
    datetime_list = []
    df_yobiritu=df_yobiritu[:]
    str_datelist = df_yobiritu['Date'].values
    str_timelist = df_yobiritu['Time'].values
    for i in range(len(df_yobiritu)):
        # 00:30始まり24:00終わりになっているため、00:00始まり23:30終わりに直す
        str_time =str_timelist[i]
        change_into_minute = int(str_time.split(':')[0])*60 + int(str_time.split(':')[1])-30
        new_hour = change_into_minute//60
        new_min = change_into_minute%60

        str_datetime = str_datelist[i]+'/'+str(new_hour) +':'+ str(new_min)
        Datetime = dt.datetime.strptime(str_datetime,'%Y/%m/%d/%H:%M')
        datetime_list.append(Datetime)
    df_yobiritu['DateTime'] = datetime_list
    # まとめるデータフレーム作成
    df_yobiritu_king = pd.DataFrame(columns=['DateTime','北海道予備率(%)','東北予備率(%)','東京予備率(%)','中部予備率(%)','北陸予備率(%)','関西予備率(%)','中国予備率(%)','四国予備率(%)','九州予備率(%)'])
    df_yobiritu_king['DateTime'] = df_yobiritu['DateTime']
    # 日付が重複しているから削除
    df_yobiritu_king = df_yobiritu_king.drop_duplicates('DateTime')
    area_list = ['北海道','東北','東京','中部','北陸','関西','中国','四国','九州']
    for area_name in area_list:

        df_yobiritu_king[f'{area_name}予備率(%)']  =df_yobiritu[df_yobiritu['エリア名']==area_name]['広域予備率(%)'].values
    df_yobiritu_king = df_yobiritu_king.reset_index(drop=True)

    return(df_yobiritu_king)


							