
*** Settings ***
Library           SeleniumLibrary
Library           helper.py
Test Teardown     Close All Browsers


*** Variables ***
${REPORT_FILE}      ${CURDIR}/report.html
${PARQUET_FOLDER}   ${CURDIR}/parquet_data/facility_type_avg_time_spent_per_visit_date
${FILTER_DATE}      2026-03-23


*** Test Cases ***
Compare Plotly Table With Parquet Data

    # Step 1: Open report.html in Chrome
    Open Browser    file://${REPORT_FILE}    chrome

    # Step 2: Wait for the page to load
    Sleep    2s

    # Step 3: Locate the table element
    ${table_element}=    Get WebElement    css:g.table

    # Step 4: Read table into DataFrame
    ${df_html}=      Read Html Table To Dataframe    ${table_element}    ${FILTER_DATE}

    # Step 5: Read Parquet data
    ${df_parquet}=   Read Parquet Data    ${PARQUET_FOLDER}    ${FILTER_DATE}

    # Step 6: Compare and pass or fail
    ${result}=       Compare Dataframes    ${df_html}    ${df_parquet}
    IF    ${result}[match] == ${False}
        Fail    ${result}[differences]
    END

    Log    SUCCESS: ${result}[differences]


