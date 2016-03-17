# Курсы валют 

## GetCursOnDate(On_date) получение курсов валют на определенную дату (ежедневные курсы валют), GetSeldCursOnDate (ежемесячные курсы валют) 
Аргументы: 
  On_date - Дата запроса для курсов, формат - System.DateTime
Результат:
XML документ в формате System.Data.Dataset, содержащий таблицу [ValuteCursOnDate], 
таблица содержит поля:

Vname - Название валюты
Vnom - Номинал
Vcurs - Курс
Vcode - Цифровой код валюты
VchCode - Символьный код валюты
результирующий DataSet содержит ExtendedProperty поле "OnDate" показывающее дату для которой присланы данные в таблице.

Справочно:

> ## EnumValutes(Seld) Справочник по кодам валют, содержит полный перечень валют котируемых Банком России.
> Аргументы: 
>   Seld - формат -boolean
> 
> False - перечень ежедневных валют
> True - перечень ежемесячных валют
> Результат:
> XML документ в формате System.Data.Dataset, содержащий таблицу [EnumValutes], 
> таблица содержит поля:
> 
> Vcode - Внутренний код валюты*
> Vname - Название валюты
> VEngname - Англ. название валюты
> Vnom - Номинал
> VcommonCode - Внутренний код валюты, являющейся 'базовой'**
> VnumCode - цифровой код ISO
> VcharCode - 3х буквенный код ISO
> *- Внутренний код - код для идентификации валют, является локальным и уникальным идентификатором валюты в данной базе, необходим для использования в качестве параметра для методов GetCursDynamic (GetCursDynamicXML).
> ** - этот код используется для связи, при изменениях кодов или названий фактически одной и той же валюты.

Получение последней даты публикации курсов валют: ежедн./ежемес. 
## GetLatestDateTime(), GetLatestDateTimeSeld() - Результат: формат - System.DateTime
## GetLatestDate(),GetLatestDateSeld() - Результат: формат - String
## GetCursDynamic(FromDate, ToDate, ValutaCode) Получение динамики ежедневных курсов валюты
Аргументы: 
FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
ValutaCode Внутренний код валюты, тип String
Результат:
XML документ в формате System.Data.Dataset, содержащий таблицу [ValuteCursDynamic], 
таблица содержит поля:

CursDate - Дата котирования
Vcode - Внутренний код валюты*
Vnom - Номинал
Vcurs - курс
* Этот код может изменяться, в случае если в запрошенном временном промежутке запрашиваемая валюта меняла название, номинал или код.

# Ставки и остатки


## DepoDynamic(FromDate, ToDate) Получение динамики ставок привлечения средств по депозитным операциям
Аргументы: 
FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
Результат:
XML документ в формате System.Data.Dataset, содержащий таблицу [Depo], 
таблица содержит поля:

DateDepo Дата
Overnight Overnight
Tom-next Tom-next
P1week 1 week
P2weeks 2 weeks
P1month 1 month
P3month 3 months
SpotNext Spot/ next
SpotWeek Spot/ week
Spot2Weeks Spot/2 weeks
CallDeposit Call Deposit

## OstatDynamic(FromDate, ToDate) Получение динамики сведений об остатках средств на корреспондентских счетах кредитных организаций XSD
Аргументы: 
FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
Результат:
XML документ в формате System.Data.Dataset, содержащий таблицу [Ostat], 
таблица содержит поля:

DateOst Дата
InRuss По России
InMoscow По Московскому региону

## OstatDepo(FromDate, ToDate) Депозиты банков в Банке России XSD
Аргументы: 
FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
Результат:
XML документ в формате System.Data.Dataset, содержащий таблицу [OD], 
таблица содержит поля:

D0 Дата
D1_7 от 1 до 7 дней
D8_30 от 8 до 30 дней
depo до востребования
total Итого
## mrrf(FromDate, ToDate) Международные резервы Российской Федерации, ежемесячные значения XSD
Аргументы: 
FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
## mrrf7D(FromDate, ToDate) Международные резервы Российской Федерации, еженедельные значения XSD
Аргументы: 
FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
## Saldo(FromDate, ToDate) Сальдо операций ЦБ РФ по предоставлению/абсорбированию ликвидности XSD
Аргументы: 
FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime

## Ruonia (FromDate, ToDate)Ставка RUONIA XSD
Аргументы: 

FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime

## ROISfix (FromDate, ToDate)Ставка ROISfix XSD
Аргументы: 

FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime

## MKR (FromDate, ToDate) Ставки межбанковского кредитного рынка XSD
Аргументы: 
FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
## DV (FromDate, ToDate) Требования Банка России к кредитным организациям XSD
Аргументы: 
FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
## Repo_debt (FromDate, ToDate) Задолженность кредитных организаций перед Банком России по операциям прямого РЕПО XSD
Аргументы: 

FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
## Overnight (FromDate, ToDate) Ставка по кредиту «overnight» (однодневный расчетный кредит) XSD
Аргументы: 

FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
## Bauction (FromDate, ToDate) База данных по размещению бюджетных средств на депозиты коммерческих банков XSD
Аргументы: 

FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime

## BiCurBase (FromDate, ToDate) Стоимость бивалютной корзины XSD
Аргументы: 

FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
## BiCurBacket() Структура бивалютной корзины XSD

