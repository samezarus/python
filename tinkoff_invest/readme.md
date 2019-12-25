Проект для Тинькофф инвестиций

Да. Да. Есть неофициальный API (python) но вот мануалов для него я не нашёл. 

Разбираться - это не мой путь. За основу возьму исходники на GO, т.к. они более лаконичные https://github.com/TinkoffCreditSystems/invest-openapi-go-sdk

Собственно всё сводится к простой отправке GET-запросов, и получения на них JSON-ответов.

Песочницу рассматривать не буду. Сразу в бой.

apiURL = 'https://api-invest.tinkoff.ru/openapi'

Portfolio
  apiURL + '/portfolio'

Market
  apiURL + '/market'

Orders
  apiURL + '/orders'

Operations
  apiURL + '/operations'
