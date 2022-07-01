#!/usr/bin/env python3
import argparse
import gzip
import zipfile
from datetime import datetime

import pandas
import xmltodict
from tabulate import tabulate


class DmarcInfoDetail(object):
    BASIC_HEADERS: list = ["SourceIP", "Count", "Disposition", "Dkim", "SPF", "Reason", "HeaderFrom", "SPFDomain", "SPFResult"]
    EXTRA_HEADERS: list = ["DKIMDomain", "DMKIResult", "DKIMSelector"]
    NUMERIC_COLUMNS: list = ["Count"]

    def __init__(self, record):
        row: dict = record['row']
        self.source_ip = row['source_ip']
        self.count = row['count']
        self.policy_evaluated_disposition = row['policy_evaluated']['disposition']
        self.policy_evaluated_dkim = row['policy_evaluated']['dkim']
        self.policy_evaluated_spf = row['policy_evaluated']['spf']
        self.policy_evaluated_reason = DmarcInfoDetail.__concatenate_reasons(row)

        self.identifiers_header_from = record['identifiers']['header_from'] if 'identifiers' in record and 'header_from' in record['identifiers'] \
            else ''

        auth_results: dict = record['auth_results']
        self.dkims: list = []
        if 'dkim' in auth_results:
            for dkim in [auth_results['dkim']] if type(auth_results['dkim']) != list else auth_results['dkim']:
                self.dkims.append({
                    'domain': dkim['domain'] if 'domain' in dkim else '',
                    'result': dkim['result'] if 'result' in dkim else '',
                    'selector': dkim['selector'] if 'selector' in dkim else ''
                })
        else:
            self.dkims.append({
                'domain': '',
                'result': '',
                'selector': ''
            })

        self.spf_domain = ''
        self.spf_result = ''
        if 'spf' in auth_results:
            self.spf_domain = auth_results['spf']['domain'] if 'domain' in auth_results['spf'] else ''
            self.spf_result = auth_results['spf']['result'] if 'result' in auth_results['spf'] else ''

    @staticmethod
    def __concatenate_reasons(row):
        reasons: list = []
        if 'reason' in row['policy_evaluated']:
            if type(row['policy_evaluated']['reason']) == list:
                reasons = row['policy_evaluated']['reason']
            else:
                reasons = [row['policy_evaluated']['reason']]

        message = ''
        for reason in reasons:
            if message != '':
                message += ' ; '

            message += ','.join([f"{k}={v}" for k, v in reason.items()])

        return message

    def plain(self):
        result: list = []
        base: list = [self.source_ip, self.count, self.policy_evaluated_disposition, self.policy_evaluated_dkim,
                      self.policy_evaluated_spf, self.policy_evaluated_reason, self.identifiers_header_from, self.spf_domain, self.spf_result]

        if len(self.dkims) > 0:
            for dkim in self.dkims:
                result.append(base + [dkim['domain'], dkim['result'], dkim['selector']])
        else:
            result.append(base)

        return result

    @staticmethod
    def get_headers(unique: bool = False):
        return DmarcInfoDetail.BASIC_HEADERS + (DmarcInfoDetail.EXTRA_HEADERS if unique else [])


class DmarcInfo(object):
    DATE_FORMAT: str = '%Y-%m-%d'
    HEADERS: list = ["Organization", "Begin", "End", "Domain", "Adkim", "Aspf", "P", "Sp", "Pct"]
    NUMERIC_COLUMNS: list = ["Pct"] + DmarcInfoDetail.NUMERIC_COLUMNS

    def __init__(self, dmarc: dict):
        metadata: dict = dmarc['feedback']['report_metadata']
        self.organization = metadata['org_name']
        self.begin_date = datetime.utcfromtimestamp(int(metadata['date_range']['begin'])).strftime(DmarcInfo.DATE_FORMAT)
        self.end_date = datetime.utcfromtimestamp(int(metadata['date_range']['end'])).strftime(DmarcInfo.DATE_FORMAT)

        policy_published: dict = dmarc['feedback']['policy_published']
        self.domain = policy_published['domain']
        self.adkim = 'strict' if 'adkim' in policy_published and policy_published['adkim'].lower() == 's' else 'relaxed'
        self.aspf = 'strict' if 'aspf' in policy_published and policy_published['aspf'].lower() == 's' else 'relaxed'
        self.p = policy_published['p'] if 'p' in policy_published else 'none'
        self.sp = policy_published['sp'] if 'sp' in policy_published else 'none'
        self.pct = policy_published['pct'] if 'pct' in policy_published else 'none'

        self.rows = []
        if type(dmarc['feedback']['record']) == list:
            reports = sorted(dmarc['feedback']['record'], key=lambda x: int(x['row']['count']), reverse=True)
        else:
            reports = [dmarc['feedback']['record']]

        for _report in reports:
            self.rows.append(DmarcInfoDetail(_report))

    def plain(self, sort_by_column: str = NUMERIC_COLUMNS[0], reverse: bool = False):
        result: list = []
        base: list = [self.organization, self.begin_date, self.end_date, self.domain,
                      self.adkim, self.aspf, self.p, self.sp, self.pct]

        for row in self.rows:
            for _row in row.plain():
                result.append(base + _row)

        return sorted(result, key=lambda x: (x[DmarcInfo.get_headers().index(sort_by_column)] if sort_by_column not in DmarcInfo.NUMERIC_COLUMNS else
                                             int(x[DmarcInfo.get_headers().index(sort_by_column)])),
                      reverse=reverse)

    @staticmethod
    def get_headers(unique: bool = False):
        return DmarcInfo.HEADERS + DmarcInfoDetail.get_headers(unique)


parser = argparse.ArgumentParser(description='Process DMARC reports')
parser.add_argument('-s', '--sort-by-column', help=f"Sort by column name, by default '{DmarcInfo.NUMERIC_COLUMNS[0]}'",
                    default=DmarcInfo.NUMERIC_COLUMNS[0], type=str)
parser.add_argument('-r', '--reverse', help="Sort in reverse order", default=False, action='store_true')
parser.add_argument('file')

args = parser.parse_args()

file = None
if zipfile.is_zipfile(args.file):
    with zipfile.ZipFile(args.file, 'r') as f:
        file = f.read(f.namelist()[0])
elif '.gz' in args.file:
    with gzip.open(args.file, 'r') as f:
        file = f.read()
elif '.xml' in args.file:
    with open(args.file, 'r') as f:
        file = f.read()
else:
    parser.error('Extension not supported')

dmarc = xmltodict.parse(file)
report: DmarcInfo = DmarcInfo(dmarc)
headers = DmarcInfo.get_headers(True)

if args.sort_by_column not in headers:
    parser.error(f"The {args.sort_by_column} is not a valid column name")

data = report.plain(args.sort_by_column, args.reverse)
index = DmarcInfo.get_headers()

df = pandas.DataFrame(data, columns=headers)
df.set_index(index)
print(tabulate(df, headers='keys', tablefmt='presto'))
