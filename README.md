# sensor nettside

Hele server mappen til nettsiden, innovasjonsprosjekt elsys, vår 2019.

Filen "__init__.py" inneholder server oppsettet. Her er alle tilatte URLer definert. Det er stort sett logikk som trengs for å gi ønsket funksjonalitet til nettsiden. 
All datahenting etc skje med funksjonskall til selvskrevet API "dbtransmit.py". 

Filen dbTransmit.py inneholder selvskrevne funksjoner (APIet) som brukes hovedsaklig til alt som har med databehandlig mot databasen og CSV filer, samt litt annet. 
Funksjonene blir kalt i "__init__.py". Funksjonaliteten til de fleste fuknsjoenen er forklart med kommentarer i koden, eller så er funksjonsnavet såpass selvforklarende at 
det ikke er nødvendig. 

I /templates ligger alle html filer som brukes til nettsiden. Filen "navbar.html" er navigasjonsbaren som inkluderes i alle html sider som vises på nettsiden. Inkludering blir gjort med 
en "{{% extends navbar.html %}}". I /static finnes alle javascript og css filer, samt bilder. Bootstrap blir brukt for responsiv og mobilvennlig nettside. 
Boostrap css er inkludert i /static/css. Boostrap js og jquery blir hostet med CDN. 

Til generering av grafer brukes highcharts.js. Oppsettet av grafene er litt ulikt etter hva slags funksjonalitet som er ønsket. Felles er at alle nødvendig highcharts filer er hostet med CDN. 
Filen charts.js brukes til å generere grafer uten realtime. Fra "__init__.py" sendes variblene til html filen, som kaller på javascriptet, som deretter genererer grafene med nevnte varaibler.
For realtime grafer brukes et 4 liknende script (en for hver graf) i html filen til å genrerere grafene med datasett fra en CSV fil.

clearRiver.py tømmer hele databasen for data. Brukt under testing. fillRiver.py fyller hele databasen med random verdier. Brukt under testing. 

mappen /static/realtimedata innholder 4 csv filer, en for hver parameter, med de siste 24 innkommende målingene. 
Disse brukes som datasett til realtime grafer som "poller" (dvs sjekker etter data) hvert andre sekund. Resten av filene er hovedsaklig blitt brukt til testing av ulike funksjoner.

Databasen som blir benyttet er en MySQL database. Denne er forhåndsinstallert på serveren. dbTransmit APIet tar seg av oppretting og sletting av tabeller etter behov. # Innovasjonsprosjekt-nettside
