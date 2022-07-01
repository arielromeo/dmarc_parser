# dmarc_parser
Pretty simple parser from DMARC XML files to table. Such table is printed out by stdout.
This does not pretend to be a fully featured script, instead, this strives to help to read and process DMARC xml files.

## References
[Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://datatracker.ietf.org/doc/html/rfc7489)

[Authentication Failure Reporting Using the Abuse Reporting Format](https://datatracker.ietf.org/doc/html/rfc6591)

[An Extensible Format for Email Feedback Reports](https://datatracker.ietf.org/doc/html/rfc5965)
## Usage
```
usage: dmarc.py [-h] [-s SORT_BY_COLUMN] [-r] file

Process DMARC reports

positional arguments:
  file

options:
  -h, --help            show this help message and exit
  -s SORT_BY_COLUMN, --sort-by-column SORT_BY_COLUMN
                        Sort by column name
  -r, --reverse         Sort in reverse order
```

## Output
```
python3 dmarc.py ~/Downloads/dmarc/emailsrvr.com\!test.com\!1656460800\!1656547200\!8d99163a-056f-4405-931e-a8a8ca6d01dd.xml

    | Organization   | Begin      | End        | Domain   | Adkim   | Aspf    | P    | Sp   |   Pct | SourceIP        |   Count | Disposition   | Dkim   | SPF   | HeaderFrom   | SPFDomain             | SPFResult   | DKIMDomain              | DMKIResult   | DKIMSelector
----+----------------+------------+------------+----------+---------+---------+------+------+-------+-----------------+---------+---------------+--------+-------+--------------+-----------------------+-------------+-------------------------+--------------+----------------
  0 | emailsrvr.com  | 2022-06-29 | 2022-06-30 | test.com | relaxed | relaxed | none | none |   100 | 54.174.63.231   |       5 | none          | pass   | pass  | test.com     | 6821985m.test.com     | pass        | 6821985m.test.com       | pass         | none
  1 | emailsrvr.com  | 2022-06-29 | 2022-06-30 | test.com | relaxed | relaxed | none | none |   100 | 54.174.63.231   |       5 | none          | pass   | pass  | test.com     | 6821985m.test.com     | pass        | test.com                | pass         | none
  2 | emailsrvr.com  | 2022-06-29 | 2022-06-30 | test.com | relaxed | relaxed | none | none |   100 | 212.146.237.209 |       3 | none          | pass   | pass  | test.com     | info.test.com         | pass        | test.com                | pass         | none
  3 | emailsrvr.com  | 2022-06-29 | 2022-06-30 | test.com | relaxed | relaxed | none | none |   100 | 3.93.157.87     |       1 | none          | pass   | fail  | test.com     | notifybf1.hubspot.com | pass        | notifybf1.hubspot.com   | pass         | none
  4 | emailsrvr.com  | 2022-06-29 | 2022-06-30 | test.com | relaxed | relaxed | none | none |   100 | 3.93.157.87     |       1 | none          | pass   | fail  | test.com     | notifybf1.hubspot.com | pass        | test.com                | pass         | none
  5 | emailsrvr.com  | 2022-06-29 | 2022-06-30 | test.com | relaxed | relaxed | none | none |   100 | 209.85.160.73   |       1 | none          | pass   | pass  | test.com     | test.com              | pass        | google.com              | pass         | none
  6 | emailsrvr.com  | 2022-06-29 | 2022-06-30 | test.com | relaxed | relaxed | none | none |   100 | 209.85.160.73   |       1 | none          | pass   | pass  | test.com     | test.com              | pass        | test.com                | pass         | none
```
