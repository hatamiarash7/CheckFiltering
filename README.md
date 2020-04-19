# Check Filtering

Check URLs that <font color='red'>filtered</font> ( or not ) in Iran

- Install requirements

```bash
python -m pip install -r requirements.txt
```

- Update `list` and add your website URLs

```
github.com
facebook.com
gitlab.com
google.com
pornhub.com
pypi.org
twitter.com
gsm.ir
xnxx.com
cloudflare.com
stackoverflow.com
```

- Run the checker

```bash
> python check.py

|-----------------|---------------|
|Address          |    Status     |
|=================================|
|github.com       |     Free      |
|-----------------|---------------|
|facebook.com     |    Blocked    |
|-----------------|---------------|
|gitlab.com       |     Free      |
|-----------------|---------------|
|google.com       |     Free      |
|-----------------|---------------|
|pornhub.com      |    Blocked    |
|-----------------|---------------|
|pypi.org         |     Free      |
|-----------------|---------------|
|twitter.com      |    Blocked    |
|-----------------|---------------|
|gsm.ir           |     Free      |
|-----------------|---------------|
|xnxx.com         |    Blocked    |
|-----------------|---------------|
|cloudflare.com   |     Free      |
|-----------------|---------------|
|stackoverflow.com|     Free      |
|-----------------|---------------|
```
