import streamlit as st
import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go

st.set_page_config(page_title="Seoul Air Pollution Dashboard", page_icon=":bar_chart:", layout="wide")

df = pd.read_csv('./seoul_data/seoul_dust_added.csv', encoding = 'cp949')
columns = df.columns

#---SIDE Bar---
st.sidebar.header("Please Filter Here: ")

user_location = st.sidebar.selectbox(
    "Select the Neighborhood:",
    options=df["Neighborhood"].unique()
)

user_year = st.sidebar.selectbox(
    "Select the Year:",
    options=df["Year"].unique()
)

user_month = st.sidebar.selectbox(
    "Select the Month:",
    options = df["Month"].unique()
)

user_day = st.sidebar.selectbox(
    "Select the Day:",
    options = df["Days"].unique()
)

# df_selection = df.query(
#    "Neighborhood == @user_location & Year == @user_year & Month == @user_month & Days == @user_day"
# )

#=================Main Page==========
#today's projected/average fine dust & microdust
st.title('😷 Seoul Air Pollution Dashboard')
st.markdown("##")

#filter only neighborhood, month, days
df_selection_average = df.query(
    "Neighborhood == @user_location & Month == @user_month & Days == @user_day"
)

average_daily = round(df_selection_average.groupby(by=["Month"]).mean(), 1).astype('int')
fd_average_daily = average_daily.iloc[0]['Finedust(PM10)'].astype('int')
micro_average_daily = average_daily.iloc[0]['Microdust(PM2.5)'].astype('int')

if (151 < fd_average_daily) or (76 < micro_average_daily):
    condition_daily = '매우나쁨 😡'
elif (81 < fd_average_daily < 150) or (36 < micro_average_daily <= 75):
    condition_daily = '나쁨 😱'
elif (fd_average_daily < 80) or (micro_average_daily < 35):
    condition_daily = '보통 😊'

st.subheader(
    f"Average air quality on {user_month}/{user_day} in {user_location}"
)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Finedust(PM10):")
    st.subheader(f"{fd_average_daily}")
with middle_column:
    st.subheader("Microdust(PM2.5):")
    st.subheader(f"{micro_average_daily}")
with right_column:
    st.subheader("Air quality:")
    st.subheader(condition_daily)
st.divider()

#=================air pollution by neighborhood==========
# Finedust BY Month [BAR CHART]
st.subheader(f"Air Pollution in {user_location}")

bar_df = df.query(
"Neighborhood == @user_location & Year == @user_year").drop(['Year', 'Days'], axis=1)

#Finedust BY days [LINE CHART]
line_df = df.query("Neighborhood == @user_location & Year == @user_year & Month == @user_month").drop(['Year', 'Month'], axis=1)

col1, col2 = st.columns(2)
with col1:
    st.caption(f'Air pollution per month in {user_year}')
    st.bar_chart(bar_df.groupby(by=["Month"]).mean())

with col2:
    st.caption(f'Air pollution by days on {user_month}월')
    st.line_chart(line_df.groupby(by=["Days"]).mean())

#Finedust BY Hours [LINE CHART]
hour_df = df.query("Neighborhood == @user_location & Year == @user_year & Month == @user_month & Days == @user_day").drop(['Year', 'Month','Days'], axis=1)
hour_df.Hour = df.Hour.apply(lambda x : x.replace(':','')).astype('int')

st.caption(f'Air pollution by hour on {user_month}/{user_day}')
st.line_chart(hour_df.groupby(by=["Hour"]).mean())

#Filtered data tabs
tab1, tab2, tab3 = st.tabs(['Year','Month','Day'])
tab1.dataframe(bar_df)
tab2.dataframe(line_df)
tab3.dataframe(hour_df)

##-----comparing different neighborhoods-----

multi_user_location = st.sidebar.multiselect(
    "Select the Neighborhood:",
    options=df["Neighborhood"].unique(),
    default=df["Neighborhood"].unique()
)

multi_user_year = st.sidebar.multiselect(
    "Select the Year:",
    options=df["Year"].unique(),
   default=df["Year"].unique()
)

df_location = df.query(
    "Neighborhood == @multi_user_location & Year == @multi_user_year"
)


# #Finedust by NEIGHBORHOOD [line]
pm_df_location = df_location.drop(['Microdust(PM2.5)','Year', 'Days'], axis=1)
pm_line_location = pm_df_location.groupby(by=["Neighborhood","Month"]).mean()

#pivot table 
pvt_pm_line_location = pm_line_location.pivot_table(index="Month", 
                              columns="Neighborhood", 
                              values="Finedust(PM10)")

#Microdust
micro_df_location = df_location.drop(['Finedust(PM10)','Year', 'Days'], axis=1)
micro_line_location = micro_df_location.groupby(by=["Neighborhood","Month"]).mean()

#pivot table 
pvt_micro_line_location = micro_line_location.pivot_table(index="Month", 
                              columns="Neighborhood", 
                              values='Microdust(PM2.5)')

st.subheader("Air pollution by neighborhood")
pm_tab, micro_tab, table = st.tabs(['Fine dust','Micro dust', 'Table'])
with pm_tab:
    st.line_chart(pvt_pm_line_location)

with micro_tab:
    st.line_chart(pvt_micro_line_location)

with table:
    st.dataframe(df_location)

#Finedust BY year [line]
df_location = df.query(
    "Neighborhood == @multi_user_location & Year == @multi_user_year"
)

pm_df_year = df_location.drop(['Microdust(PM2.5)', 'Days'], axis=1)
pm_line_year = pm_df_year.groupby(by=["Year","Month"]).mean()

#pivot table 
pvt_pm_line_year = pm_line_year.pivot_table(index="Month", 
                              columns="Year", 
                              values="Finedust(PM10)")

#Microdust
micro_df_year = df_location.drop(['Finedust(PM10)', 'Days'], axis=1)
micro_line_year = micro_df_year.groupby(by=["Year","Month"]).mean()

#pivot table 
pvt_micro_line_year = micro_line_year.pivot_table(index="Month", 
                              columns="Year", 
                              values='Microdust(PM2.5)')

st.subheader(f"Air pollution by years")
pm_tab, micro_tab, table = st.tabs(['Fine dust','Micro dust', 'Table'])
with pm_tab:
    st.line_chart(pvt_pm_line_year)

with micro_tab:
    st.line_chart(pvt_micro_line_year)

with table:
    st.dataframe(df_location)


#---Overview Table & Graph---
st.divider()

group_by_cols = df.columns[0:3] 
result_cols = df.columns[3:5]

group_by_option = st.selectbox('Group By:', ['None'] + list(group_by_cols))
cols = st.multiselect('컬럼 선택:', list(result_cols))

if group_by_option == 'None':
    if cols:
        tmp_df = df[cols] # if none is selected -> all columns
    else:
        tmp_df = df
else: # groupby를 할 컬럼이 선택된 경우
    if cols:
        tmp_df = df.groupby(group_by_option).mean()[cols]
    else:
        tmp_df = df.groupby(group_by_option).mean()

plot_tab, df_tab = st.tabs(['Plot', 'Table'])
with plot_tab:
    st.line_chart(tmp_df)
with df_tab:
    st.dataframe(tmp_df)

