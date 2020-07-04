# smhirain
Custom component for home assistant, smhi rain last day sensor

Find station close to you here:
https://www.smhi.se/vadret/vadret-i-sverige/observationer#ws=wpt-a,proxy=wpt-a,tab=vader,param=t

Click a station and see it's id, enter in station in configuration

Add this to configuration.yaml
```
sensor:
  - platform: smhirain
    station: '53430'
```
