# cf-dns-update-python
Dynamic DNS record update utility for CloudFlare DNS service. Python implement

### Requirements

- Linux/macOS (tested with macOS 10.15.1 & Ubuntu 18.04)
- Python 3 ( version >= 3.6 is recommended )

### Download & Setup

#### Download
Download code from Release page. 

Link here: [https://github.com/nhymxu/cf-dns-update-python/releases/latest](https://github.com/nhymxu/cf-dns-update-python/releases/latest)

Or 

clone repo using git:

```shell
git clone git@github.com:nhymxu/cf-dns-update-python.git
```

#### Create CloudFlare Token

1. Go to CloudFlare dash
2. Click open any domain you have
3. Scroll to bottom, you can see **API** section from right column.
4. Click `Get your API token`
5. Click `Create Token`
6. Enter Token name
7. On `Permissions` section. Choose `Zone` - `DNS` - `Edit`
8. On `Zone resource` section. Choose `Include` - `All zone` or specific zone you want.
9. Click `Continue to Summary`
10. Copy token display on page

#### Setup CloudFlare Token

Copy file `config.ini.sample` to current folder with name `config.ini`

Add CloudFlare token to first section like this

```ini
[common]
CF_API_TOKEN = token_key_here
```

#### Setup record to update

1. Look at step **3** on section `Create CloudFlare Token`
2. Copy `Zone ID`
3. Add to `config.ini` like this:

```ini
[dungnt.net]
zone_id = zone_id_here
record = test.dungnt.net
```

### Auto running

I want my script auto running every `x` minutes. So I need set up cronjob for it.

From server shell, typing:

```shell
crontab -e
```

And add this line to end of file

```text
*/15 * * * * /opt/cf-dns-update-python/run.sh
```

This script will run each 15 minutes.
