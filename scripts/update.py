#!/usr/bin/env python3
"""Refresh this repo from VeritaHire's daily list: https://veritahire.com/data/lists/us-internships.json
(rebuilt every morning about 05:50 UTC from live jobs re-checked on employers' own career sites).

Writes data/jobs.json, data/jobs.csv and the README block between <!-- jobs:start --> and <!-- jobs:end -->.
Standard library only, so the GitHub Action needs no installs.
"""
import csv, io, json, os, urllib.request

SRC = 'https://veritahire.com/data/lists/us-internships.json'
UA = {'User-Agent': 'us-internships-updater (+https://github.com/veritahire/us-internships)'}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLS = ['title', 'employer', 'location', 'remote', 'employment_type', 'pay_as_posted', 'first_seen', 'last_confirmed', 'url']
TYPES = {'full_time': 'Full-time', 'part_time': 'Part-time', 'internship': 'Internship', 'contract': 'Contract',
          'seasonal': 'Seasonal', 'temporary': 'Temporary'}


def cell(s):
    return (str(s) if s is not None else '').replace('|', '/').replace('\n', ' ').strip()


def main():
    with urllib.request.urlopen(urllib.request.Request(SRC, headers=UA), timeout=60) as r:
        doc = json.loads(r.read().decode('utf-8'))
    jobs = doc.get('jobs') or []
    if len(jobs) < 10:
        raise SystemExit('refusing to publish a list of %d rows' % len(jobs))
    os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
    with open(os.path.join(ROOT, 'data', 'jobs.json'), 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, extrasaction='ignore', lineterminator='\n')
    w.writeheader()
    w.writerows(jobs)
    with open(os.path.join(ROOT, 'data', 'jobs.csv'), 'w', encoding='utf-8', newline='') as f:
        f.write(buf.getvalue())
    lines = ['**%d jobs**, updated %s. Every one was confirmed on the employer\'s own career site in the last 3 days.'
             % (len(jobs), doc.get('generated_at', '')[:10]), '',
             '| Role | Employer | Location | Pay (as posted) | Type | Posted | |',
             '|---|---|---|---|---|---|---|']
    for j in jobs:
        lines.append('| %s | %s | %s | %s | %s | %s | [View](%s) |' % (
            cell(j.get('title')), cell(j.get('employer')), cell(j.get('location')), cell(j.get('pay_as_posted')) or '-',
            TYPES.get(j.get('employment_type') or '', '-'), cell(j.get('first_seen')), j.get('url')))
    p = os.path.join(ROOT, 'README.md')
    t = open(p, encoding='utf-8').read()
    a, b = t.index('<!-- jobs:start -->') + len('<!-- jobs:start -->'), t.index('<!-- jobs:end -->')
    open(p, 'w', encoding='utf-8').write(t[:a] + '\n' + '\n'.join(lines) + '\n' + t[b:])
    with open(os.path.join(ROOT, 'data', 'count.txt'), 'w') as f:
        f.write('%d %s\n' % (len(jobs), doc.get('generated_at', '')))


if __name__ == '__main__':
    main()
