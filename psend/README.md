# Psend cog
Pushover notification cog.

This cog sends you notifications with Pushover.

## Usage

### Set your server-wide Pushover API token (requires server manager permissions)

```
[p]setapitoken <api_token>
```

### Set your personal Pushover client token
```
[p]settoken <client_token>
```

### Send a push message!
```
[p]psend <message="Message from <server_name> Discord">
```

### Send a URL
Psend will find the title for the website you're sending and use that as the push title.
```
[p]psend https://www.google.com/
```

### Send an image
Paste an image into Discord and add a comment of `[p]psend`.

## Installation

### Load the Downloader cog

```
[p]load downloader
```

### Add the repo

```
[p]repo add fallenby https://github.com/fallenby/redbot_cogs.git
```

### Install the cog

```
[p]cog install fallenby psend
```

### Load the cog

```
[p]load psend
```