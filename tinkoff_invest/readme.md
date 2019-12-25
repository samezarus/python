Проект для Тинькофф инвестиций

Да. Да. Есть неофициальный API (python) но вот мануалов для него я не нашёл. 

Разбираться - это не мой путь. За основу возьму исходники на GO, т.к. они более лаконичные https://github.com/TinkoffCreditSystems/invest-openapi-go-sdk

Собственно всё сводится к простой отправке GET-запросов, и получения на них JSON-ответов.

Песочницу рассматривать не буду. Сразу в бой.

apiURL = 'https://api-invest.tinkoff.ru/openapi'

Portfolio

	apiURL + '/portfolio'
	
	apiURL + '/portfolio/currencies'

Market

	apiURL + '/market'
	
	apiURL + '/market/bonds'
	
	apiURL + '/market/currencies'
	
	apiURL + '/market/etfs'
	
	apiURL + '/market/stocks'
	
	apiURL + '/market/search/by-figi?figi=' + figi

Orders

	apiURL + '/orders'

Operations

	apiURL + '/operations'

