# dmc-date-reminder

Collaborative notification of important dates through various forms of communications protocols and devices so we don't miss stuff. 

## datereminder.py

The original GladOS, reads content from the "DMC Important Dates (GLaDOS)" Google Sheet.

Will only process a line if it has content in the `mm-dd` `type` `channel` `days prior` and `text` columns.

Handle `birthday` and `work anniversary` `type`.

Configuration file in `~/.datereminder/config.yml`

    icon_emoji: ':glados:'
    username: GladOS
    webhook: webhook_url_as_given_by_slack
    downloadurl: 'Google_sheet_url/gviz/tq?tqx=out:csv&sheet=Google_sheet_tab'


Note that the `downloadurl` need to be readable by anybody with the link since the script can not login as a user. It also downloads a CVS file to work from.
the link can be creatd by select the google doc, File > Share > Publish to the Web ... and select csv format.
or url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&id={sheet_id}&gid={gid}'
where gid isually 0, sheet_id is the actual sheetId
## datereminder_ms.py

The modified version of the tool, designed to read the "DMC-Master Deliverable Schedule" Google Sheet.

Will only process a line of it has content in the `date` `name` and `program` columns.

Default values are to publish in the `#dmc-deliverables` `channel`, with 10 `days prior` and 10 `days post` (if a value is present in those columns, it will override the default value).

The icon displayed depends on the status of the deliverable and if any content is present in the `submitted on` column.

Configuration file in `~/.datereminder/config_ms.yml` follow similar rules as for the above script with the added `presenturl` which provides a link to the original sheet.
