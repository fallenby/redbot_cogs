# COVID cog
COVID19 stat cog.

This cog provides the most-recent COVID19 stats for a given country, defaulting to South Africa.

This cog uses the [COVID19 GraphQL QPI](https://github.com/rlindskog/covid19-graphql).

## Usage

```
[p]covid [country=South Africa]
```
e.g.
```
[p]covid "United Kingdom"
```

### Example display

![COVID19 stats for South Africa](https://i.gyazo.com/82f8dc4dc38bf262d6b861091737a56a.png)

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
[p]cog install fallenby covid
```

### Load the cog

```
[p]load covid
```