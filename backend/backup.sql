--
-- PostgreSQL database dump
--

\restrict VjX3rhDTl1yrws8ATbuttKqDsrybWmDEcjKfZDWZwrZ9wsOIGk2Bf0U3hR40KHC

-- Dumped from database version 18.3 (Ubuntu 18.3-1.pgdg24.04+1)
-- Dumped by pg_dump version 18.3 (Ubuntu 18.3-1.pgdg24.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: budget_level; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.budget_level AS ENUM (
    'low',
    'medium',
    'high'
);


ALTER TYPE public.budget_level OWNER TO postgres;

--
-- Name: poi_status_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.poi_status_enum AS ENUM (
    'main',
    'additional'
);


ALTER TYPE public.poi_status_enum OWNER TO postgres;

--
-- Name: trip_purpose; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.trip_purpose AS ENUM (
    'leisure',
    'business',
    'education',
    'other'
);


ALTER TYPE public.trip_purpose OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: cities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cities (
    id uuid NOT NULL,
    country_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    content text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.cities OWNER TO postgres;

--
-- Name: city_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.city_rules (
    city_id uuid NOT NULL,
    rule_id uuid NOT NULL,
    is_strict boolean NOT NULL
);


ALTER TABLE public.city_rules OWNER TO postgres;

--
-- Name: countries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.countries (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    content text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.countries OWNER TO postgres;

--
-- Name: country_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.country_rules (
    country_id uuid NOT NULL,
    rule_id uuid NOT NULL,
    is_strict boolean NOT NULL
);


ALTER TABLE public.country_rules OWNER TO postgres;

--
-- Name: poi_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.poi_rules (
    poi_id uuid NOT NULL,
    rule_id uuid NOT NULL,
    is_strict boolean NOT NULL
);


ALTER TABLE public.poi_rules OWNER TO postgres;

--
-- Name: pois; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pois (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    information text,
    geom public.geometry(Point,4326),
    is_indoor boolean NOT NULL,
    city_id uuid NOT NULL,
    google_place_id character varying(255)
);


ALTER TABLE public.pois OWNER TO postgres;

--
-- Name: rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rules (
    id uuid NOT NULL,
    content text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.rules OWNER TO postgres;

--
-- Name: trip_pois; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trip_pois (
    trip_id uuid NOT NULL,
    poi_id uuid NOT NULL,
    sequence_order double precision,
    planned_start_time timestamp with time zone,
    poi_status public.poi_status_enum DEFAULT 'main'::public.poi_status_enum NOT NULL,
    is_selected boolean DEFAULT false NOT NULL,
    day_number integer,
    CONSTRAINT chk_trip_pois_order CHECK ((sequence_order > (0)::double precision))
);


ALTER TABLE public.trip_pois OWNER TO postgres;

--
-- Name: trips; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trips (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    country_id uuid NOT NULL,
    city_id uuid NOT NULL,
    purpose public.trip_purpose NOT NULL,
    budget public.budget_level NOT NULL,
    group_size integer NOT NULL,
    other_information character varying[],
    start_date date,
    end_date date,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_trips_dates CHECK ((end_date >= start_date)),
    CONSTRAINT chk_trips_group_size CHECK ((group_size >= 1))
);


ALTER TABLE public.trips OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    email character varying(254) NOT NULL,
    hashed_password character varying(60) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
74b6e9839d4e
\.


--
-- Data for Name: cities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cities (id, country_id, name, content, created_at, updated_at) FROM stdin;
72df7555-6cda-41ca-8269-11b0d4885703	30891716-033e-41ad-9893-631af79ad11a	Гуанчжоу	Гуанчжоу — один из крупнейших торговых городов Китая на юге страны. Известен оптовыми рынками одежды, электроники и товаров. Метро хорошо развито, билет стоит 2–12 юаней. Ночные рынки работают до 23:00–00:00. Лучшее время для посещения — октябрь–апрель, летом очень жарко и влажно.	2026-03-20 22:40:20.013814	2026-03-20 22:40:20.013814
812714b9-873b-41b9-b849-acb601551000	30891716-033e-41ad-9893-631af79ad11a	Шэньчжэнь	Шэньчжэнь — современный технологический город рядом с Гонконгом. Граница с Гонконгом через переход Lok Ma Chau — один из самых загруженных в мире. Метро соединяет город с пограничными переходами. Валюта — юань, в приграничных районах принимают гонконгский доллар.	2026-03-20 22:40:20.013814	2026-03-20 22:40:20.013814
6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	30891716-033e-41ad-9893-631af79ad11a	Сиань	Сиань — древняя столица Китая, начальная точка Великого шёлкового пути. Главная достопримечательность — Терракотовая армия, 30 км от центра. Мусульманский квартал — обязательное место для посещения с уличной едой. Городская стена полностью сохранилась, можно арендовать велосипед. Добраться до Терракотовой армии: автобус №5 или туристический автобус от ж/д вокзала.	2026-03-20 22:40:20.013814	2026-03-20 22:40:20.013814
79318373-6e9a-4b91-8201-e2736508b269	30891716-033e-41ad-9893-631af79ad11a	Чжанцзяцзе	Чжанцзяцзе — национальный парк с уникальными скалами-столбами, ставшими прообразом планеты Пандора в фильме Аватар. Рекомендуется выделить минимум 3–4 дня на посещение парка. Лучший сезон — весна (апрель–май) и осень (сентябрь–ноябрь). Зимой меньше туристов, красивый туман, но часть аттракционов закрыта.	2026-03-20 22:40:20.013814	2026-03-20 22:40:20.013814
29d7e71c-3f97-4ee0-a349-6d991c977e31	30891716-033e-41ad-9893-631af79ad11a	Фэнхуан	Фэнхуан — древний город с хорошо сохранившейся архитектурой эпохи Мин и Цин. Расположен в ~40 минутах езды на поезде от Чжанцзяцзе — удобно совмещать. Деревянные дома на сваях над рекой Туцзян — главная визитная карточка города. Вход в старый город платный — около 148 юаней.	2026-03-20 22:40:20.013814	2026-03-20 22:40:20.013814
87d60596-c253-42b6-8983-2cfbf427996c	30891716-033e-41ad-9893-631af79ad11a	Чунцин	Чунцин — мегаполис на слиянии рек Янцзы и Цзялин, известный острой кухней и сложным рельефом с эскалаторами прямо в жилых кварталах. Знаменит барбекю хого (горячий горшок) — местная гастрономическая традиция. Панорамные виды на ночной город — одни из лучших в Китае.	2026-03-20 22:40:20.013814	2026-03-20 22:40:20.013814
5a5725ee-c783-49ae-85aa-15e86e0e9f71	30891716-033e-41ad-9893-631af79ad11a	Фошань	Фошань — промышленный город рядом с Гуанчжоу, известный производством мебели, керамики и текстиля. Район Наньхай известен аутлет-центрами с брендовыми товарами. До Гуанчжоу — 30 минут на метро или автобусе.	2026-03-20 22:40:20.013814	2026-03-20 22:40:20.013814
5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	e9e5cf1f-f4fc-4563-8ebb-2110f14cf5b8	Киото	Культурное сердце Японии, знаменитое своими тысячами красных торий храма Фусими Инари, Золотым павильоном и умиротворяющими бамбуковыми рощами Арасияма[cite: 2].	2026-03-26 15:32:15.93246	2026-03-26 15:32:15.93246
f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	e9e5cf1f-f4fc-4563-8ebb-2110f14cf5b8	Осака	Динамичный город, известный своим историческим замком XVI века, ярким гастрономическим районом Дотонбори и парком Universal Studios Japan[cite: 2].	2026-03-26 15:32:46.916676	2026-03-26 15:32:46.916676
82788d97-9e68-4975-9812-8d81bd71ce37	cceb7c00-55e5-42c3-9f8e-f3388e8e1127	Сеул	Энергичная столица, объединяющая величие дворца Кёнбоккун эпохи Чосон с современными торговыми улицами Мёндон и панорамными видами с башни N Seoul Tower[cite: 2].	2026-03-26 15:33:40.785179	2026-03-26 15:33:40.785179
8717ad74-80b9-4ac4-9640-bc1308ad3081	0afc0ac8-f6dc-4ff6-a69b-c1c79923ca50	Бангкок	Шумная столица на реке Чаупхрая, дом для священного Изумрудного Будды, величественного Храма Рассвета и гигантских рынков выходного дня[cite: 2].	2026-03-26 15:34:35.219107	2026-03-26 15:34:35.219107
f3e4f111-f0ec-4f7c-a3a7-2eaeb68a674e	0afc0ac8-f6dc-4ff6-a69b-c1c79923ca50	Пхукет	Главный островной курорт страны, предлагающий доступ к островам Пхи-Пхи, историческую застройку Старого города и величественную статую Большого Будды[cite: 2].	2026-03-26 15:34:52.68538	2026-03-26 15:34:52.68538
7b2a2673-2a59-40aa-b097-c2b46a72c95f	e9e5cf1f-f4fc-4563-8ebb-2110f14cf5b8	Токио	Ультрасовременный мегаполис, где неоновые небоскребы Сибуя соседствуют с древним храмом Сэнсо-дзи[cite: 2]. Это город контрастов, предлагающий всё: от иммерсивного цифрового искусства в TeamLab до традиционных рыбных рынков[cite: 2].	2026-03-26 15:51:49.583865	2026-03-26 15:51:49.583865
9a6c21db-8538-4721-bce9-96a06e37b368	cceb7c00-55e5-42c3-9f8e-f3388e8e1127	Пусан	Крупный портовый город с живописными пляжами Хэундэ, красочной культурной деревней Камчхон и крупнейшим в Корее рыбным рынком Чагальчхи[cite: 2].	2026-03-26 15:52:28.759901	2026-03-26 15:52:28.759901
\.


--
-- Data for Name: city_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.city_rules (city_id, rule_id, is_strict) FROM stdin;
72df7555-6cda-41ca-8269-11b0d4885703	b08921f6-e410-46e6-ba4d-9b69ae68d8a1	f
72df7555-6cda-41ca-8269-11b0d4885703	aa860e95-fc35-4797-bafc-9b1d6aa9bee6	f
72df7555-6cda-41ca-8269-11b0d4885703	f5f021b1-eb78-4a57-8a01-e51a8318ef02	f
6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	655de729-10bb-4cff-b3c3-d4ba4c4a6f45	t
6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	6412be1d-03ca-4a4d-943f-8cf9d77d2ceb	t
6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	2bd923f3-8e25-42a8-b668-7ce82113f8d3	t
79318373-6e9a-4b91-8201-e2736508b269	e8eab6eb-70c0-4950-9215-c26c72ffc9b5	t
79318373-6e9a-4b91-8201-e2736508b269	46b5b542-8c1c-46c2-bdbd-5eff5e8df97f	f
79318373-6e9a-4b91-8201-e2736508b269	a56041f9-de39-4be4-8961-6c10a6828462	f
29d7e71c-3f97-4ee0-a349-6d991c977e31	d0cfb217-7014-49fa-8f77-d9b7a771e1cf	t
29d7e71c-3f97-4ee0-a349-6d991c977e31	39a097d4-398d-4914-bae5-1eef229c10fb	t
87d60596-c253-42b6-8983-2cfbf427996c	8fb42674-e130-4b18-97d5-c2cc00bbc6cf	t
87d60596-c253-42b6-8983-2cfbf427996c	1896319d-6be5-4a01-a27a-8ff4b113346b	f
5a5725ee-c783-49ae-85aa-15e86e0e9f71	473436c0-8d81-4f46-a1f8-c5a4375c4626	f
5a5725ee-c783-49ae-85aa-15e86e0e9f71	33112d57-4418-4d16-89f5-6f8dcee7c4de	f
812714b9-873b-41b9-b849-acb601551000	5fa990d0-0f0a-436d-9549-50be62fd0d50	f
812714b9-873b-41b9-b849-acb601551000	132d4917-4332-4770-91a8-e5ef0f394034	t
\.


--
-- Data for Name: countries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.countries (id, name, content, created_at, updated_at) FROM stdin;
30891716-033e-41ad-9893-631af79ad11a	Китай	Китай — самая населённая страна мира с богатейшей историей более 5000 лет. Официальный язык — мандаринский китайский. Валюта — юань (CNY). Виза обязательна для большинства стран, оформляется заранее. Интернет ограничен — Google, Instagram, WhatsApp заблокированы. Рекомендуется установить VPN до въезда в страну. Основной способ оплаты — WeChat Pay и Alipay, наличные принимаются везде. Иностранные карты работают ограниченно — лучше иметь наличные юани.	2026-03-20 22:40:19.952777	2026-03-20 22:40:19.952777
e9e5cf1f-f4fc-4563-8ebb-2110f14cf5b8	Япония	Страна восходящего солнца, где древние синтоистские храмы соседствуют с неоновыми небоскребами, а вековые традиции — с передовыми технологиями.	2026-03-26 15:25:48.888548	2026-03-26 15:25:48.888548
cceb7c00-55e5-42c3-9f8e-f3388e8e1127	Южная Корея	Динамичное государство, объединяющее богатое историческое наследие эпохи Чосон с современными трендами, K-pop культурой и потрясающей кухней.	2026-03-26 15:26:06.628359	2026-03-26 15:26:06.628359
0afc0ac8-f6dc-4ff6-a69b-c1c79923ca50	Таиланд	Тропический рай Юго-Восточной Азии, известный своими белоснежными пляжами, древними буддийскими святынями и неповторимым колоритом уличной жизни.	2026-03-26 15:26:21.706554	2026-03-26 15:26:21.706554
\.


--
-- Data for Name: country_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.country_rules (country_id, rule_id, is_strict) FROM stdin;
30891716-033e-41ad-9893-631af79ad11a	6d07f900-290c-480b-8830-4b3815185e66	t
30891716-033e-41ad-9893-631af79ad11a	933121d5-f487-40ae-b1a5-7ed29b87aef5	t
30891716-033e-41ad-9893-631af79ad11a	24024f55-150f-472f-9374-fcd20af1ebe3	t
30891716-033e-41ad-9893-631af79ad11a	eefeb451-c2b6-4ded-ba51-8f5ca736c933	t
30891716-033e-41ad-9893-631af79ad11a	241710c5-e2c1-4c50-94e4-ed55329571ff	f
\.


--
-- Data for Name: poi_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.poi_rules (poi_id, rule_id, is_strict) FROM stdin;
\.


--
-- Data for Name: pois; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pois (id, name, description, information, geom, is_indoor, city_id, google_place_id) FROM stdin;
7844c291-e741-4f5b-a22d-59506e0fb743	Florence Village	Establishment, point of interest	Рейтинг Google: 4.3 (36 отзывов). Адрес: 28 Shu Gang Lu, 28, Nan Hai Qu, Fo Shan Shi, Guang Dong Sheng, Китай, 528251	0101000020E610000058AD4CF8A54E5C40287E8CB96B013740	t	5a5725ee-c783-49ae-85aa-15e86e0e9f71	\N
d4828061-1a90-4d8c-a278-5c748843ce14	Wanguo Outlet	Establishment, point of interest	Рейтинг Google: 4.2 (182 отзывов). Адрес: 40 Qian Jin Lu, Hai Zhu Qu, Guang Zhou Shi, Guang Dong Sheng, Китай, 510240	0101000020E61000005DC2A1B778515C408CF678211D1A3740	t	72df7555-6cda-41ca-8269-11b0d4885703	\N
1b717083-e685-46ab-9371-0a3fd5b1c6da	Night Markets	Establishment, point of interest	Рейтинг Google: 4.1 (15403 отзывов). Адрес: Guangzhou St, Wanhua District, Taipei City, Тайвань 108	0101000020E61000007F6374E5D85F5E40D7BFEB3367093940	f	72df7555-6cda-41ca-8269-11b0d4885703	\N
0b4396ec-c9bd-4b8a-9a52-a3218505e5fa	Party Pier	Establishment, point of interest	Рейтинг Google: 4.6 (208 отзывов). Адрес: 485R+283, Yue Jiang Xi Lu, Hai Zhu Qu, Guang Zhou Shi, Guang Dong Sheng, Китай, 510308	0101000020E61000008A75AA7CCF555C40FD885FB1861B3740	f	72df7555-6cda-41ca-8269-11b0d4885703	\N
fc3d34d6-6ba2-457e-87a6-b0af9df0ac7c	YIML Garment Market	Clothing store, establishment	Рейтинг Google: 4.5 (17 отзывов). Адрес: 11 Zhan Nan Lu, Yue Xiu Qu, Guang Zhou Shi, Guang Dong Sheng, Китай, 510499	0101000020E6100000611BF16437505C40E2ADF36F97253740	t	72df7555-6cda-41ca-8269-11b0d4885703	\N
82a3ee30-ecaf-4b1e-a65f-b488b6768a18	Baima Garment Market	Establishment, point of interest	Рейтинг Google: 4.4 (573 отзывов). Адрес: 16 Zhan Nan Lu, Yue Xiu Qu, Guang Zhou Shi, Guang Dong Sheng, Китай, 510499	0101000020E61000008997A77345505C405725917D90253740	t	72df7555-6cda-41ca-8269-11b0d4885703	\N
74632aca-fe88-49ca-8198-9b54586aa63b	Lok Ma Chau	Neighborhood, political	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Lok Ma Chau, Гонконг	0101000020E61000006D3CD86237855C4020459DB987823640	f	812714b9-873b-41b9-b849-acb601551000	\N
05673645-201c-4432-8848-d959f904450e	Zhangjiajie National Forest Park	Establishment, park	Рейтинг Google: 4.7 (1132 отзывов). Адрес: Wulingyuan District, Zhangjiajie, Hunan, Китай, 427403	0101000020E61000005298F738D39B5B40E94317D4B7503D40	f	79318373-6e9a-4b91-8201-e2736508b269	\N
7f7be6af-0073-4647-97db-ffbbf0c7f3e4	Wally House	Establishment, lodging	Рейтинг Google: 5 (2 отзывов). Адрес: 500 m from Biaozhimen Entrance, 军邸路武陵源区张家界市湖南省 Китай, 427000	0101000020E61000006C04E275FDA25B400A815CE2C85B3D40	t	79318373-6e9a-4b91-8201-e2736508b269	\N
149df31a-f6f1-43bc-a7ae-1f84b9dff8fd	Jiezhi Hotel	Establishment, lodging	Рейтинг Google: 4 (1 отзывов). Адрес: Китай, Hu Nan Sheng, Zhang Jia Jie Shi, Wu Ling Yuan Qu, 未央路9H42+FJR 邮政编码: 427000	0101000020E6100000D3307C444CA35B40903B6C22335B3D40	t	79318373-6e9a-4b91-8201-e2736508b269	\N
2defbbce-b7f6-4428-bd47-f7e063053ea9	Fenghuang Ancient Town	Political, sublocality	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Fenghuang County, Xiangxi Tujia and Miao Autonomous Prefecture, Hunan, Китай	0101000020E6100000BC22F8DF4A665B406E0C4B4DCCF23B40	f	29d7e71c-3f97-4ee0-a349-6d991c977e31	\N
16a9949a-c13e-42a5-9b11-d63bcb540c20	Terracotta Army	Establishment, museum	Рейтинг Google: 4.6 (7680 отзывов). Адрес: Lintong District, Xi'An, Shaanxi, Китай, 710612	0101000020E6100000114D45CFD2515B4055B2ADB02A314140	t	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
7adea094-ff80-44ca-a1ca-98302514ba21	Giant Wild Goose Pagoda	Establishment, place of worship	Рейтинг Google: 4.5 (973 отзывов). Адрес: 1 Ci En Lu, Yan Ta Qu, Xi An Shi, Shan Xi Sheng, Китай, 710064	0101000020E61000004A58C0A9B43D5B401A097E65EF1B4140	f	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
53a6559e-1392-4b6d-97c8-bee50de58b8f	Bell and Drum Towers	Establishment, point of interest	Рейтинг Google: 4.6 (160 отзывов). Адрес: 7W6V+8C4, Bei Yuan Men, 北院门小吃一条街 Lian Hu Qu, Xi An Shi, Shan Xi Sheng, Китай, 710008	0101000020E6100000F743C769633C5B40874F3A9160214140	f	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
5473c473-7bd7-4217-9e73-4d1babc3829a	Xi'an City Wall	Establishment, point of interest	Рейтинг Google: 4.6 (998 отзывов). Адрес: Xincheng, Сиань, Китай, 710003	0101000020E61000008B1BB7989F3C5B402159C0046E234140	f	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
8e250fde-95ca-4cf4-9e12-23edb4dfa9fa	Muslim Quarter	Establishment, point of interest	Рейтинг Google: 4.5 (175 отзывов). Адрес: 90 Bei Guang Ji Jie, 钟楼商圈 Lian Hu Qu, Xi An Shi, Shan Xi Sheng, Китай, 710008	0101000020E6100000DDB1D826153C5B4016FC36C478214140	f	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
ab5fd4e1-0eb2-46d4-a5f1-c26b8f601c23	Forest of Steles Museum	Establishment, museum	Рейтинг Google: 4.4 (291 отзывов). Адрес: 15 San Xue Jie, Bei Lin Qu, Xi An Shi, Shan Xi Sheng, Китай, 710001	0101000020E6100000689599D2FA3C5B405A4A969350204140	t	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
96796225-e752-4ed4-8a7a-39cb29f29799	Ding Laotou BBQ	Establishment, food	Рейтинг Google: 5 (1 отзывов). Адрес: PC32+WJ2, Ren Min Dong Lu, Fu Ling Qu, Chong Qing Shi, Китай, 408005	0101000020E61000005D876A4AB2D95A4005C24EB16AB43D40	t	87d60596-c253-42b6-8983-2cfbf427996c	\N
60874813-4cbb-473b-954e-48c0e0804d23	Senso-ji Temple	Establishment, place of worship	Рейтинг Google: 4.5 (92729 отзывов). Адрес: 2-chōme-3-1 Asakusa, Taito City, Tokyo 111-0032, Япония	0101000020E6100000EC7541337E7961403D693C6C7DDB4140	f	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
c2047c0a-02c4-48b0-9c52-86719f6f95fd	Shibuya Crossing	Establishment, point of interest	Рейтинг Google: 4.5 (19287 отзывов). Адрес: 21 Удагаватё, Сибуя, Токио 150-0042, Япония	0101000020E6100000C35CF7FB6A7661407C26FBE769D44140	f	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
f74decc4-8294-4dc4-9a0f-a47fa21464a1	Tokyo Tower	Art gallery, establishment	Рейтинг Google: 4.5 (94632 отзывов). Адрес: 4-chōme-2-8 Shibakōen, Minato City, Tokyo 105-0011, Япония	0101000020E610000099DB1896DA77614044A4A65D4CD44140	f	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
17416ae4-a40e-4dd9-9b21-f757fb12dfcb	Tsukiji Fish Market	Establishment, point of interest	Рейтинг Google: 4.2 (55404 отзывов). Адрес: Япония, 〒104-0045 Tokyo, Chuo City, Tsukiji, 4-chōme−16 および６丁目一部	0101000020E61000003D4679E6A578614012ED743117D54140	f	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
ca6920d3-f8d9-49b9-b89c-683ed9aeae6a	TeamLab Planets	Amusement park, establishment	Рейтинг Google: 4.5 (49925 отзывов). Адрес: 6-chōme-1-16 Toyosu, Koto City, Tokyo 135-0061, Япония	0101000020E610000080F7E9D3457961400CD4186316D34140	t	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
610bbd25-d493-487a-9fcd-936bf5ae19b8	Fushimi Inari Shrine	Establishment, place of worship	Рейтинг Google: 4.6 (85934 отзывов). Адрес: 68 Fukakusa Yabunouchichō, Fushimi Ward, Kyoto, 612-0882, Япония	0101000020E61000005C6ED51AEFF860407102D369DD7B4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
411ef3bc-2f8d-42f5-8d30-1513872c3150	Kinkaku-ji	Establishment, place of worship	Рейтинг Google: 4.5 (66313 отзывов). Адрес: 1 Kinkakujichō, Kita Ward, Kyoto, 603-8361, Япония	0101000020E6100000AD2AA0F555F76040C5387F130A854140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
dd44000e-8b8a-4a71-8081-e8301bc38025	Arashiyama Bamboo Grove	Establishment, park	Рейтинг Google: 4.3 (21118 отзывов). Адрес: Сагаогураяма Табутияматё, Укё, Киото, 616-8394, Япония	0101000020E61000006528DD4C7BF560400A3B7B1D27824140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
7e6089cf-433e-4397-8011-0b4b318ad396	Osaka Castle	Establishment, museum	Рейтинг Google: 4.4 (93027 отзывов). Адрес: 1-1 Ōsakajō, Chuo Ward, Osaka, 540-0002, Япония	0101000020E610000070AE06CDD3F06040CE38680AF8574140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
31c8b07b-5460-4d3a-9bd5-067b6c6a811b	Dotonbori	Political, sublocality	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Дотомбори, Chuo Ward, Осака, 542-0071, Япония	0101000020E61000008B259B6119F060405A88693A96554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
49994beb-86d5-4209-9350-935e29a66770	Universal Studios Japan	Amusement park, establishment	Рейтинг Google: 4.5 (149194 отзывов). Адрес: 2-chōme-1-33 Sakurajima, Konohana Ward, Osaka, 554-0031, Япония	0101000020E6100000965E9B8DD5ED60405CDABAE534554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
ea4c5864-b155-469b-8690-61ba31189cc2	Gyeongbokgung Palace	Establishment, point of interest	Рейтинг Google: 4.6 (46051 отзывов). Адрес: 161 Sajik-ro, Jongno District, Seoul, Южная Корея	0101000020E61000007976F9D687BE5F40529ACDE330CA4240	f	82788d97-9e68-4975-9812-8d81bd71ce37	\N
61533264-11db-4128-b1b9-83922b0abb53	N Seoul Tower	Establishment, point of interest	Рейтинг Google: 4.5 (66222 отзывов). Адрес: 105 Namsangongwon-gil, Yongsan District, Seoul, Южная Корея	0101000020E61000006302C81A3FBF5F4029C709B88CC64240	f	82788d97-9e68-4975-9812-8d81bd71ce37	\N
2a19766e-ff0a-4159-970f-463ba5c2d87c	Myeongdong Shopping Street	Establishment, point of interest	Рейтинг Google: 4.3 (1139 отзывов). Адрес: 1-5 Myeong-dong, Jung District, Seoul, Южная Корея	0101000020E6100000CEFFAB8E1CBF5F40C0232A5437C84240	f	82788d97-9e68-4975-9812-8d81bd71ce37	\N
6c4c5415-9515-4bd7-8912-f88a933c3dfc	Bukchon Hanok Village	Establishment, landmark	Рейтинг Google: 4.4 (23826 отзывов). Адрес: Gyedong-gil, Jongno District, Seoul, Южная Корея	0101000020E610000084A8B17309BF5F4021CF89986DCA4240	f	82788d97-9e68-4975-9812-8d81bd71ce37	\N
03021a09-98d3-4faf-97d1-bab2aa6e2168	Haeundae Beach	Establishment, natural feature	Рейтинг Google: 4.6 (2626 отзывов). Адрес: Haeundae Beach, Южная Корея	0101000020E610000072B90BDE212560407E3A1E3350944140	f	9a6c21db-8538-4721-bce9-96a06e37b368	\N
dd64f2c4-ed97-4917-bbdb-a63c46af1c55	Gamcheon Culture Village	Establishment, point of interest	Рейтинг Google: 4.4 (31751 отзывов). Адрес: 203 Gamnae 2-ro, Saha-gu, Busan, Южная Корея	0101000020E6100000C272DFC556206040E178E349778C4140	f	9a6c21db-8538-4721-bce9-96a06e37b368	\N
5ce8ee5b-1294-4703-83f6-191e8609b553	Jagalchi Fish Market	Establishment, food	Рейтинг Google: 4 (26676 отзывов). Адрес: 52 Jagalchihaean-ro, Jung-gu, Busan, Южная Корея	0101000020E61000009A0AF148FC206040AC17E87F5E8C4140	f	9a6c21db-8538-4721-bce9-96a06e37b368	\N
3b62206c-42cd-4f81-92e5-c9a2c2414e20	Wat Phra Kaew	Establishment, place of worship	Рейтинг Google: 4.7 (42343 отзывов). Адрес: Na Phra Lan Rd, Khwaeng Phra Borom Maha Ratchawang, Khet Phra Nakhon, Krung Thep Maha Nakhon 10200, Таиланд	0101000020E6100000BA06C776881F59408080B56AD7802B40	f	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
709a596b-1ee2-4a9e-be7e-a6b8cbe12c9f	Wat Arun	Establishment, place of worship	Рейтинг Google: 4.7 (43830 отзывов). Адрес: 158 Thanon Wang Doem, Khwaeng Wat Arun, Khet Bangkok Yai, Krung Thep Maha Nakhon 10600, Таиланд	0101000020E61000005B7B9FAA421F5940D74345E6DB7C2B40	f	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
ca6cc99a-f0aa-464b-806f-9ff13073c1ac	Chatuchak Market	Establishment, point of interest	Рейтинг Google: 4.4 (55053 отзывов). Адрес: 587, 10 Kamphaeng Phet 2 Rd, Khwaeng Chatuchak, Khet Chatuchak, Krung Thep Maha Nakhon 10900, Таиланд	0101000020E6100000B39AAE273A235940A2EC2DE57C992B40	f	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
af119f05-462d-49d9-b282-8ce6940ee3e9	ICONSIAM	Establishment, point of interest	Рейтинг Google: 4.7 (56652 отзывов). Адрес: 299 Charoen Nakhon Rd, Khwaeng Khlong Ton Sai, Khet Khlong San, Krung Thep Maha Nakhon 10600, Таиланд	0101000020E61000005FECBDF8A2205940FA4DBC5EF5732B40	t	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
a2f0c839-3432-4668-90a4-86f2c1452b9d	Phi Phi Islands	Establishment, natural feature	Рейтинг Google: 4.6 (7417 отзывов). Адрес: Пхипхи, Mueang Krabi District, Краби, Таиланд	0101000020E610000047382D78D1B15840289EB30584F61E40	f	f3e4f111-f0ec-4f7c-a3a7-2eaeb68a674e	\N
229da484-15af-4d9b-88bd-5b4ae6e0ac3e	Big Buddha Phuket	Establishment, place of worship	Рейтинг Google: 4.6 (37950 отзывов). Адрес: Тамбон Карон, Столичный ампхе Пхукет, Пхукет 83100, Таиланд	0101000020E61000008CD3B59B059458405BC75D29704F1F40	f	f3e4f111-f0ec-4f7c-a3a7-2eaeb68a674e	\N
5f69f593-3c47-481e-aadc-ec2a971fd4cc	Old Phuket Town	Neighborhood, political	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Old Phuket Town, Mueang Phuket District, Phuket 83000, Таиланд	0101000020E610000044B2DBC2CE98584072A83A3F208B1F40	f	f3e4f111-f0ec-4f7c-a3a7-2eaeb68a674e	\N
d14c666c-9295-494b-bf00-9e86e078674e	COCO Park	Establishment, point of interest	Рейтинг Google: 4.3 (877 отзывов). Адрес: 268 Fu Hua San Lu, 中心城 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518020	0101000020E610000049D576137C835C40FF3EE3C281883640	f	812714b9-873b-41b9-b849-acb601551000	\N
0f4169ed-5f79-45ae-9574-77b171a82296	Ancestral Temple (Zumiao)	Premise, street address	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Zu Miao, 桂城 Chan Cheng Qu, Fo Shan Shi, Guang Dong Sheng, Китай, 528011	0101000020E6100000C3899E4A3C475C40C284D1AC6C073740	f	5a5725ee-c783-49ae-85aa-15e86e0e9f71	\N
016936b0-7417-4cfc-aaa8-2a7e38bd23b5	Nanfeng Ancient Kiln	Establishment, point of interest	Рейтинг Google: 4.8 (4 отзывов). Адрес: 234H+789, Gao Miao Lu, Chan Cheng Qu, Fo Shan Shi, Guang Dong Sheng, Китай, 528031	0101000020E61000002254A9D903455C40F5F57CCD72013740	f	5a5725ee-c783-49ae-85aa-15e86e0e9f71	\N
bb1f6269-1ebd-44a8-8c07-dbeb747e2f9e	Liang's Garden	Establishment, point of interest	Рейтинг Google: 5 (1 отзывов). Адрес: 29PM+2FQ, Da Xue Cheng Wai Huan Xi Lu, Pan Yu Qu, Guang Zhou Shi, Guang Dong Sheng, Китай, 510006	0101000020E6100000B18A37328F585C403EE8D9ACFA083740	f	5a5725ee-c783-49ae-85aa-15e86e0e9f71	\N
a6c4f47c-094a-470b-939f-ccda451936d1	Xiqiao Mountain	Establishment, natural feature	Рейтинг Google: 4.6 (29 отзывов). Адрес: Mount Xiqiao, Nanhai District, Foshan, Китай, 528208	0101000020E6100000AE47E17A143E5C40A76ED34444F43640	f	5a5725ee-c783-49ae-85aa-15e86e0e9f71	\N
3199fd69-49f7-4748-9605-94199da3c522	Wong Fei-hung Memorial Hall	Establishment, museum	Рейтинг Google: 4.5 (141 отзывов). Адрес: 24H7+84F, Zu Miao Lu, 祖庙顺德区 Fo Shan Shi, Guang Dong Sheng, Китай, 528011	0101000020E6100000844DF80038475C4021E527D53E073740	t	5a5725ee-c783-49ae-85aa-15e86e0e9f71	\N
3a414d37-4144-4222-a013-1533a5d9e8da	Shunde Qinghui Garden	Establishment, park	Рейтинг Google: 4.3 (186 отзывов). Адрес: 23 Qing Hui Lu, Shun De Qu, Fo Shan Shi, Guang Dong Sheng, Китай, 528300	0101000020E6100000CA6FD1C952505C40349F73B7EBD53640	f	5a5725ee-c783-49ae-85aa-15e86e0e9f71	\N
cecbe274-cfaa-4901-9935-989a4f062379	Florence Village	Establishment, point of interest	Рейтинг Google: 4.3 (36 отзывов). Адрес: 28 Shu Gang Lu, 28, Nan Hai Qu, Fo Shan Shi, Guang Dong Sheng, Китай, 528251	0101000020E610000058AD4CF8A54E5C40287E8CB96B013740	t	5a5725ee-c783-49ae-85aa-15e86e0e9f71	\N
ca000f1d-8e29-4c10-8de2-b201f74bc40f	Bruce Lee Ancestral House	Establishment, point of interest	Рейтинг Google: 4.6 (20 отзывов). Адрес: P4CG+HHP, Jun'anzhen, Shunde District, Foshan, Guangdong Province, Китай, 528329	0101000020E6100000003ACC9717485C40465F419AB1B83640	t	5a5725ee-c783-49ae-85aa-15e86e0e9f71	\N
c19f4746-89ff-456f-9314-4b51a43e10ca	Sanshui Lotus World	Establishment, point of interest	Рейтинг Google: 4.6 (5 отзывов). Адрес: Китай, Guang Dong Sheng, Fo Shan Shi, San Shui Qu, 南丰大道5WW4+G5C 邮政编码: 528100	0101000020E610000061F426D0F1395C408BA94FCD40323740	f	5a5725ee-c783-49ae-85aa-15e86e0e9f71	\N
37621f1d-a8fb-46d3-9c20-bbe391094d41	Lingnan Tiandi	Establishment, point of interest	Рейтинг Google: 4.9 (8 отзывов). Адрес: 24H7+JXW, Dong Xi Li, 祖庙 Chan Cheng Qu, Fo Shan Shi, Guang Dong Sheng, Китай, 528011	0101000020E61000000150C58D5B475C4036B1C05774073740	f	5a5725ee-c783-49ae-85aa-15e86e0e9f71	\N
c1552b84-d331-410b-bd49-e0ce69784839	Canton Tower	Establishment, point of interest	Рейтинг Google: 4.6 (1031 отзывов). Адрес: Yue Jiang Xi Lu, Hai Zhu Qu, Guang Zhou Shi, Guang Dong Sheng, Китай, 510308	0101000020E6100000EE5FB422C5555C40FEF0F3DF831B3740	t	72df7555-6cda-41ca-8269-11b0d4885703	\N
2d2b3d60-d2e8-4bc5-afaf-9e92d195f8f7	Chen Clan Ancestral Hall	Establishment, museum	Рейтинг Google: 4.5 (1266 отзывов). Адрес: Китай, Guang Dong Sheng, Guang Zhou Shi, Li Wan Qu, 中山七八路恩龙里34号 邮政编码: 510040	0101000020E610000059784DFE5D4F5C408CAF87403F213740	t	72df7555-6cda-41ca-8269-11b0d4885703	\N
08507a57-f91c-4d01-9717-3ae1c2d8b030	Yuexiu Park	Establishment, park	Рейтинг Google: 4.5 (1007 отзывов). Адрес: 988 Jie Fang Bei Lu, Yue Xiu Qu, Guang Zhou Shi, Guang Dong Sheng, Китай, 510040	0101000020E6100000ADF6B0170A515C409BE3DC26DC233740	f	72df7555-6cda-41ca-8269-11b0d4885703	\N
06ad83e7-bfac-458f-9e14-3d257e3f4c1e	Shamian Island	Establishment, natural feature	Рейтинг Google: 4.6 (172 отзывов). Адрес: Shamiandao Island, 沙面 Liwan District, Guangzhou, Китай, 510130	0101000020E61000006D814E52AA4F5C408C457820571B3740	f	72df7555-6cda-41ca-8269-11b0d4885703	\N
e65bb8fc-1396-49eb-882b-23ace89f169e	Baiyun Mountain	Establishment, natural feature	Рейтинг Google: 4.6 (96 отзывов). Адрес: Байюньшань, Baiyun, Гуанчжоу, Китай, 510599	0101000020E61000004A99D4D006535C40ED9BFBABC72D3740	f	72df7555-6cda-41ca-8269-11b0d4885703	\N
a0929563-2938-4eac-bf2c-7d9eb9b6afb8	Sacred Heart Cathedral	Establishment, point of interest	Рейтинг Google: 4.6 (146 отзывов). Адрес: 56 Jiu Bu Qian, Yue Xiu Qu, Guang Zhou Shi, Китай, 510120	0101000020E610000046425BCEA5505C404CE0D6DD3C1D3740	t	72df7555-6cda-41ca-8269-11b0d4885703	\N
f5b3a5f5-8c6d-483a-8b64-47d8faf981f2	Chimelong Safari Park	Establishment, park	Рейтинг Google: 4.5 (282 отзывов). Адрес: Китай, Guang Dong Sheng, Guang Zhou Shi, Pan Yu Qu, 105国道 邮政编码: 511445	0101000020E6100000E4F90CA837545C405303CDE7DC013740	f	72df7555-6cda-41ca-8269-11b0d4885703	\N
e355082f-f2d9-4a43-8fda-640a3c1b3f56	Baima Garment Market	Establishment, point of interest	Рейтинг Google: 4.4 (573 отзывов). Адрес: 16 Zhan Nan Lu, Yue Xiu Qu, Guang Zhou Shi, Guang Dong Sheng, Китай, 510499	0101000020E61000008997A77345505C405725917D90253740	t	72df7555-6cda-41ca-8269-11b0d4885703	\N
be1f657c-4dc3-4182-9a6f-44bc92cfbd00	Pearl River Night Cruise	Establishment, point of interest	Рейтинг Google: 4.5 (51 отзывов). Адрес: 4753+33R, Yan Jiang Xi Lu, 南方大厦 Li Wan Qu, Guang Zhou Shi, Guang Dong Sheng, Китай, 510123	0101000020E61000000EA48B4D2B505C40D2AA9674941B3740	f	72df7555-6cda-41ca-8269-11b0d4885703	\N
c31df26d-139e-486b-95c4-4b49f9e0bcac	Museum of the Mausoleum of the Nanyue King	Premise, street address	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Xi Han Nan Yue Wang Bo Wu Guan - Zhuan Ti Zhan Lan Ting, 兰圃 Yue Xiu Qu, Guang Zhou Shi, Guang Dong Sheng, Китай, 510040	0101000020E610000012A3E716BA505C400B39002C3C233740	t	72df7555-6cda-41ca-8269-11b0d4885703	\N
7a9ccaaf-3b96-4b7d-a485-a426c4b6a279	Window of the World	Establishment, point of interest	Рейтинг Google: 4.5 (90 отзывов). Адрес: GXPG+46Q, Shen Nan Da Dao, 华侨城 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518058	0101000020E6100000BB2BBB60707E5C4071AAB5300B893640	f	812714b9-873b-41b9-b849-acb601551000	\N
b8c7de24-1617-48d7-9b46-ee3d71fd56e6	Splendid China Folk Village	Amusement park, establishment	Рейтинг Google: 4.4 (142 отзывов). Адрес: Unnamed Road, GXJQ+FFX华侨城南山区深圳市广东省 Китай, 518053	0101000020E61000004D1AFE2E477F5C408F78680EFF873640	f	812714b9-873b-41b9-b849-acb601551000	\N
7303694a-eee4-455d-8989-31e71ca9e762	Ping An Finance Centre	Establishment, point of interest	Рейтинг Google: 4.6 (593 отзывов). Адрес: 中心城 Futian District, Шэньчжэнь, Китай, 518017	0101000020E61000006DFFCA4A93835C40E0A0BDFA78883640	t	812714b9-873b-41b9-b849-acb601551000	\N
6d326d4b-1847-4166-9b01-464c051b0d5a	OCT-LOFT Creative Culture Park	Establishment, point of interest	Рейтинг Google: 3.6 (8 отзывов). Адрес: G28V+RW8, Yi Hao Lu, 新洲 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518042	0101000020E6100000F3C64961DE825C40842EE1D05B843640	f	812714b9-873b-41b9-b849-acb601551000	\N
e0d98b06-2da5-4a1c-8856-39620d11bcd9	Fairy Lake Botanical Garden	Establishment, point of interest	Рейтинг Google: 4.2 (220 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 仙湖路160号 邮政编码: 518004	0101000020E610000006A79949AF8B5C401E328A8ADD933640	f	812714b9-873b-41b9-b849-acb601551000	\N
74b60c23-747b-4ca3-97c8-af2b97d24b4f	Huaqiangbei Electronics Market	Electronics store, establishment	Рейтинг Google: 4.4 (343 отзывов). Адрес: 1015 Hua Qiang Bei Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518028	0101000020E6100000C9E369F981855C402BB92F0CFD8A3640	t	812714b9-873b-41b9-b849-acb601551000	\N
6b10c4ab-1af5-43c3-ab97-ca31d28fdb3b	Coco Park	Establishment, point of interest	Рейтинг Google: 4.3 (877 отзывов). Адрес: 268 Fu Hua San Lu, 中心城 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518020	0101000020E610000049D576137C835C40FF3EE3C281883640	t	812714b9-873b-41b9-b849-acb601551000	\N
80a51eb1-324e-4053-a67d-4ae36258b925	Shenzhen Museum	Establishment, museum	Рейтинг Google: 4.8 (9 отзывов). Адрес: 4001 Jin Tian Lu, 中心城 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518047	0101000020E610000034B9BD49F8835C4072D98DE32C8B3640	t	812714b9-873b-41b9-b849-acb601551000	\N
bb2ed172-fffd-42f3-8cc4-d873f033811e	Sea World Shekou	Establishment, point of interest	Рейтинг Google: 4.5 (476 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, Nanyou, 太子路 邮政编码: 518060	0101000020E6100000E3FE23D3A17A5C40DD7BB8E4B87B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
d3a241d2-439c-40a0-bf32-a91393ad8f0a	Dafen Oil Painting Village	Establishment, lodging	Рейтинг Google: 4.4 (193 отзывов). Адрес: Longgang, Шэньчжэнь, Китай, 518112	0101000020E6100000889FFF1EBC885C400EA14ACD1E9C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
16c8ee3d-8aac-44a6-9011-45d3decb26b9	Tianmen Mountain	Establishment, natural feature	Рейтинг Google: 4.7 (898 отзывов). Адрес: Тяньмэнь, Yongding District, Чжанцзяцзе, Китай, 427302	0101000020E6100000317BD976DA9E5B409128B4ACFB0B3D40	f	79318373-6e9a-4b91-8201-e2736508b269	\N
a45a65d9-0086-4516-8ccd-635a387e7465	Yuanjiajie	Political, sublocality	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Yuanjiajie, Wulingyuan District, Zhangjiajie, Hunan, Китай, 427400	0101000020E610000052616C21C8A25B403C4B9011503D3D40	f	79318373-6e9a-4b91-8201-e2736508b269	\N
4f57cdc0-f03e-4aa4-9c3b-087bf0364f89	Yellow Dragon Cave	Establishment, point of interest	Рейтинг Google: 4.5 (483 отзывов). Адрес: Китай, Hu Nan Sheng, Zhang Jia Jie Shi, Wu Ling Yuan Qu, 索溪峪镇河口村9J77+5XP 邮政编码: 427499	0101000020E61000004EED0C535BA75B4094C151F2EA5C3D40	t	79318373-6e9a-4b91-8201-e2736508b269	\N
8b50792a-b18f-4ad4-9a20-8c037da6f8aa	Baofeng Lake	Establishment, natural feature	Рейтинг Google: 4.2 (91 отзывов). Адрес: Baofeng Lake, Wulingyuan District, Zhangjiajie, Китай, 427499	0101000020E6100000635FB2F160A35B40AFEE586C93523D40	f	79318373-6e9a-4b91-8201-e2736508b269	\N
d1fadde0-48a5-489b-b2bc-f150a3c1e0df	Zhangjiajie Glass Bridge	Establishment, point of interest	Рейтинг Google: 4.5 (2627 отзывов). Адрес: Китай, 湖南省张家界市武陵源区9MXW+7FP 邮政编码: 427234	0101000020E61000002E7E09CB8EAC5B4079C3C771F1653D40	f	79318373-6e9a-4b91-8201-e2736508b269	\N
5162130a-5139-4b9b-b950-07031c537452	Golden Whip Stream	Establishment, point of interest	Рейтинг Google: 4.7 (135 отзывов). Адрес: 8C9J+R73, Wulingyuan District, Zhangjiajie, Hunan, Китай, 427403	0101000020E610000039268BFB8F9B5B40D9942BBCCB513D40	f	79318373-6e9a-4b91-8201-e2736508b269	\N
be6149b6-2828-4bde-a299-c9c897459eef	Ten-mile Gallery	Establishment, point of interest	Рейтинг Google: 4.4 (409 отзывов). Адрес: 9F7Q+C6R, Wulingyuan District, Zhangjiajie, Hunan, Китай, 427401	0101000020E610000076AAD7883B9F5B4089230F44165D3D40	f	79318373-6e9a-4b91-8201-e2736508b269	\N
af165175-9481-4543-8fb5-d29bd2d83b03	Tujia Folk Customs Park	Establishment, park	Рейтинг Google: 4.3 (342 отзывов). Адрес: Китай, Hu Nan Sheng, Zhang Jia Jie Shi, Yong Ding Qu, 306省道南庄坪 邮政编码: 427000	0101000020E6100000ED612F14B09D5B40BC067DE9ED1F3D40	f	79318373-6e9a-4b91-8201-e2736508b269	\N
35a20020-76df-4c11-bde5-9a7f1419a850	Yangjiajie	Political, sublocality	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Yangjiajie, Yongding District, Zhangjiajie, Hunan, Китай, 427209	0101000020E61000009A42E73576B55B40E5B33C0FEE163D40	f	79318373-6e9a-4b91-8201-e2736508b269	\N
8e1d9afc-3735-4ab9-b975-27c123fae685	Бёдо-ин	Establishment, place of worship	Рейтинг Google: 4.5 (21760 отзывов). Адрес: Renge-116 Uji, Kyoto 611-0021, Япония	0101000020E61000000B862980D8F960401C51EB47D4714140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
f51d90a7-dbd1-4b6d-8178-b2b395e8792f	Tianzi Mountain	Establishment, point of interest	Рейтинг Google: 4.7 (55 отзывов). Адрес: 9FH7+PFC, Wulingyuan District, Zhangjiajie, Hunan, Китай, 427401	0101000020E61000001F680586AC9D5B40E09EE74F1B613D40	f	79318373-6e9a-4b91-8201-e2736508b269	\N
b871d89b-7811-4f7e-8add-71224a5246ce	Terracotta Army	Establishment, museum	Рейтинг Google: 4.6 (7680 отзывов). Адрес: Lintong District, Xi'An, Shaanxi, Китай, 710612	0101000020E6100000114D45CFD2515B4055B2ADB02A314140	t	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
48aea130-045e-49ff-9db0-32a06bf84d9c	Ancient City Wall	Establishment, point of interest	Рейтинг Google: 4.6 (397 отзывов). Адрес: Китай, Shan Xi Sheng, Xi An Shi, Bei Lin Qu, 陕西 邮政编码: 710001	0101000020E61000002A1F82AAD13C5B406CCCEB8843204140	f	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
821f3fa2-ab10-40d2-b525-e1770f8a746b	Giant Wild Goose Pagoda	Establishment, place of worship	Рейтинг Google: 4.5 (973 отзывов). Адрес: 1 Ci En Lu, Yan Ta Qu, Xi An Shi, Shan Xi Sheng, Китай, 710064	0101000020E61000004A58C0A9B43D5B401A097E65EF1B4140	f	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
58aabe9b-83cc-43da-9956-a9095d78afd6	Muslim Quarter	Establishment, point of interest	Рейтинг Google: 4.5 (175 отзывов). Адрес: 90 Bei Guang Ji Jie, 钟楼商圈 Lian Hu Qu, Xi An Shi, Shan Xi Sheng, Китай, 710008	0101000020E6100000DDB1D826153C5B4016FC36C478214140	f	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
b653b780-2fa1-4550-aec1-3b9a597ed750	Bell Tower	Establishment, point of interest	Рейтинг Google: 4.5 (618 отзывов). Адрес: 7W5W+QRJ, Beilin, Сиань, Шэньси, Китай, 710007	0101000020E6100000BC0A84F89B3C5B4055736F3436214140	t	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
1e85640f-2096-43fc-9fd7-1dff4d5067c4	Drum Tower	Establishment, point of interest	Рейтинг Google: 4.5 (75 отзывов). Адрес: 6WQR+2QV, Jian Fu Si Lu, Bei Lin Qu, Xi An Shi, Shan Xi Sheng, Китай, 710064	0101000020E6100000DB899290483C5B40ACAA97DF691E4140	t	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
26d97c01-e022-4703-97d0-feb558417c7d	Shaanxi History Museum	Establishment, museum	Рейтинг Google: 4.3 (559 отзывов). Адрес: 91 Xiao Zhai Dong Lu, Yan Ta Qu, Xi An Shi, Shan Xi Sheng, Китай, 710064	0101000020E6100000CAFB389A233D5B403F00A94D9C1C4140	t	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
c10537b4-6a03-4b34-bf65-81caedcb1bac	Stele Forest	Establishment, museum	Рейтинг Google: 4.4 (291 отзывов). Адрес: 15 San Xue Jie, Bei Lin Qu, Xi An Shi, Shan Xi Sheng, Китай, 710001	0101000020E6100000689599D2FA3C5B405A4A969350204140	t	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
a49c2d91-26e4-43a5-95dd-d9ec7f426126	Small Wild Goose Pagoda	Establishment, place of worship	Рейтинг Google: 4.5 (432 отзывов). Адрес: 72 You Yi Xi Lu, Bei Lin Qu, Xi An Shi, Shan Xi Sheng, Китай, 710064	0101000020E61000006FB9FAB1493C5B40C1AA7AF99D1E4140	f	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
210b2f68-7f72-4adf-b3a2-1e30803e58d4	Huaqing Palace	Establishment, point of interest	Рейтинг Google: 4.4 (50 отзывов). Адрес: Китай, Shan Xi Sheng, Xi An Shi, Lin Tong Qu, Hua Qing Lu, 华清路 邮政编码: 710699	0101000020E6100000BB7D5699A94D5B40439D03159F2E4140	f	6ea12fdc-c2a4-4ed4-ba46-edc049da7db4	\N
bd8f79ad-b5fd-4505-ba58-93b28dc13e52	Hongya Cave	Establishment, point of interest	Рейтинг Google: 4.5 (701 отзывов). Адрес: Юйчжун, Китай, 400011	0101000020E61000001B66683C11A55A407F6C921FF18F3D40	f	87d60596-c253-42b6-8983-2cfbf427996c	\N
c225b93b-68fd-4265-ab3e-3a1945cfc80b	Ciqikou Ancient Town	Establishment, point of interest	Рейтинг Google: 4.3 (865 отзывов). Адрес: Шапинба, Китай, 400038	0101000020E610000077103B53E89C5A4082A966D652943D40	f	87d60596-c253-42b6-8983-2cfbf427996c	\N
43d5f44b-1528-44fb-ae3b-7f1592e7ebee	Jiefangbei Central Business District	Establishment, point of interest	Рейтинг Google: 4.7 (30 отзывов). Адрес: Китай, Chong Qing Shi, Yu Zhong Qu, 邹容路 邮政编码: 400011	0101000020E6100000A27C410B09A55A40234910AE808E3D40	f	87d60596-c253-42b6-8983-2cfbf427996c	\N
e7218793-79dd-46af-ad79-8c76522fd548	Three Gorges Museum	Establishment, museum	Рейтинг Google: 4.2 (333 отзывов). Адрес: 236 Ren Min Lu, Daxigou, Yu Zhong Qu, Chong Qing Shi, Китай, 400015	0101000020E61000007DCC07043AA35A404A42226DE38F3D40	t	87d60596-c253-42b6-8983-2cfbf427996c	\N
599cfe12-0666-4211-9245-46d9cc6afd39	Liziba Station	Establishment, point of interest	Рейтинг Google: 4.4 (263 отзывов). Адрес: Китай, Chong Qing Shi, Yu Zhong Qu, 35, 正北方向50米 邮政编码: 400015	0101000020E610000026FC523F6FA25A404B1FBAA0BE8D3D40	f	87d60596-c253-42b6-8983-2cfbf427996c	\N
57f4ac2a-46b7-42f8-bdc0-518a2e92b2da	Yangtze River Cableway	Establishment, point of interest	Рейтинг Google: 4 (202 отзывов). Адрес: HH5M+34J, Xin Hua Lu, Yu Zhong Qu, Chong Qing Shi, Китай, 400012	0101000020E61000006E6B0BCF4BA55A404EF2237EC58E3D40	f	87d60596-c253-42b6-8983-2cfbf427996c	\N
177a2acc-adbc-4f25-8515-99684e822186	Eling Park	Establishment, park	Рейтинг Google: 4.3 (248 отзывов). Адрес: 181 E Ling Zheng Jie, Yu Zhong Qu, Chong Qing Shi, Китай, 400014	0101000020E6100000185B087250A25A40944DB9C2BB8C3D40	f	87d60596-c253-42b6-8983-2cfbf427996c	\N
da7e03ac-67d9-4d5b-a9df-a4c9e58355cb	Chongqing Zoo	Establishment, point of interest	Рейтинг Google: 4.3 (679 отзывов). Адрес: 杨家坪 Цзюлунпо, Китай, 400051	0101000020E61000006FF3C64961A05A4000AC8E1CE9803D40	f	87d60596-c253-42b6-8983-2cfbf427996c	\N
6780a8b4-c389-4a47-842a-f328c20ca274	Raffles City Chongqing	Establishment, point of interest	Рейтинг Google: 4.6 (293 отзывов). Адрес: HH7Q+9CC, Chang Jiang Bin Jiang Lu, Chaotianmen, Yu Zhong Qu, Chong Qing Shi, Китай, 400013	0101000020E6100000B519A721AAA55A4093A641D13C903D40	t	87d60596-c253-42b6-8983-2cfbf427996c	\N
c07f084d-e2c8-4109-afba-bd86b40ee338	Dazu Rock Carvings	Establishment, point of interest	Рейтинг Google: 4.8 (185 отзывов). Адрес: Дацзу, Китай, 402586	0101000020E610000094A46B26DF725A40E9B81AD995BE3D40	f	87d60596-c253-42b6-8983-2cfbf427996c	\N
052a80a7-7882-4bbf-b476-1796d3efdefe	Senso-ji Temple	Establishment, place of worship	Рейтинг Google: 4.5 (92730 отзывов). Адрес: 2-chōme-3-1 Asakusa, Taito City, Tokyo 111-0032, Япония	0101000020E6100000EC7541337E7961403D693C6C7DDB4140	f	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
6ca60032-7a9a-49e1-bbe8-82460b07dd77	Tokyo Skytree	Establishment, point of interest	Рейтинг Google: 4.4 (112059 отзывов). Адрес: 1-chōme-1-2 Oshiage, Sumida City, Tokyo 131-0045, Япония	0101000020E6100000551BF741F1796140034EA555E3DA4140	t	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
c05f0d52-383a-46c8-be1f-8f5b6918265e	Meiji Jingu Shrine	Establishment, place of worship	Рейтинг Google: 4.6 (48987 отзывов). Адрес: 1-1 Yoyogikamizonochō, Shibuya, Tokyo 151-8557, Япония	0101000020E6100000DDB7B5E060766140E48B513294D64140	f	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
fd82a8da-3506-4c9a-bb7a-4a6a249ca84e	Shibuya Crossing	Establishment, point of interest	Рейтинг Google: 4.5 (19287 отзывов). Адрес: 21 Удагаватё, Сибуя, Токио 150-0042, Япония	0101000020E6100000C35CF7FB6A7661407C26FBE769D44140	f	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
c19db208-16e5-4d9e-ae6d-273bb3e98a94	Ueno Park	Establishment, park	Рейтинг Google: 4.4 (33296 отзывов). Адрес: 4 Уэнокоэн, Тайто, Токио 110-0007, Япония	0101000020E610000098B6C9F2BF7861409610621D7DDB4140	f	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
c15fd539-7b73-4a47-9982-fc99b47e56f6	Akihabara Electric Town	Colloquial area, political	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Akihabara Electric Town, Tokyo, Япония	0101000020E61000006273C410AF7861400B1EF00A8ED94140	f	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
78a4f50b-37d3-4eda-bb2a-0bd314c5259b	Ghibli Museum	Establishment, museum	Рейтинг Google: 4.5 (18796 отзывов). Адрес: 1-chōme-1-83 Shimorenjaku, Mitaka, Tokyo 181-0013, Япония	0101000020E61000004103FBF940726140C11DA8531ED94140	t	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
336b9e7d-5c6b-4d61-8576-9236057b90fc	TeamLab Planets	Amusement park, establishment	Рейтинг Google: 4.5 (49926 отзывов). Адрес: 6-chōme-1-16 Toyosu, Koto City, Tokyo 135-0061, Япония	0101000020E610000080F7E9D3457961400CD4186316D34140	t	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
c5a611ea-3a6f-4d79-a83e-a85032496b4a	Ryosho	Establishment, food	Рейтинг Google: 4.8 (78 отзывов). Адрес: 570-166 Gionmachi Minamigawa, Higashiyama Ward, Kyoto, 605-0074, Япония	0101000020E61000006DB713DBD3F8604072EEC04A4F804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
b7edec2c-6dfb-4a60-a59c-5a5a861b5bc2	Tsukiji Outer Market	Establishment, point of interest	Рейтинг Google: 4.2 (55404 отзывов). Адрес: Япония, 〒104-0045 Tokyo, Chuo City, Tsukiji, 4-chōme−16 および６丁目一部	0101000020E61000003D4679E6A578614012ED743117D54140	f	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
f5fe29d9-74fc-43a9-a78f-8d3358c3fcb0	Shinjuku Gyoen	Establishment, park	Рейтинг Google: 4.6 (43587 отзывов). Адрес: 11 Naitōmachi, Shinjuku City, Tokyo 160-0014, Япония	0101000020E610000004BF57BEB8766140433F64DBB3D74140	f	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
46f79ac0-6384-421d-bf27-a87d1ae0e4ae	Gyeongbokgung Palace	Establishment, point of interest	Рейтинг Google: 4.6 (46051 отзывов). Адрес: 161 Sajik-ro, Jongno District, Seoul, Южная Корея	0101000020E61000007976F9D687BE5F40529ACDE330CA4240	f	82788d97-9e68-4975-9812-8d81bd71ce37	\N
3ca7972f-720b-471e-9d51-195f664a9b5b	Bukchon Hanok Village	Establishment, landmark	Рейтинг Google: 4.4 (23824 отзывов). Адрес: Gyedong-gil, Jongno District, Seoul, Южная Корея	0101000020E610000084A8B17309BF5F4021CF89986DCA4240	f	82788d97-9e68-4975-9812-8d81bd71ce37	\N
0fb45923-89f8-48a0-9fe9-268466e84feb	N Seoul Tower	Establishment, point of interest	Рейтинг Google: 4.5 (66225 отзывов). Адрес: 105 Namsangongwon-gil, Yongsan District, Seoul, Южная Корея	0101000020E61000006302C81A3FBF5F4029C709B88CC64240	t	82788d97-9e68-4975-9812-8d81bd71ce37	\N
3be5db6c-a8fc-406d-b71e-6d163d99042e	Myeongdong	Political, sublocality	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Улица Мёндон, Jung District, Сеул, Южная Корея	0101000020E610000071DB08D517BF5F400135B56CADC74240	f	82788d97-9e68-4975-9812-8d81bd71ce37	\N
bba48916-61fd-47ee-ac18-8d555272c298	Dongdaemun Design Plaza	Establishment, point of interest	Рейтинг Google: 4.3 (31264 отзывов). Адрес: 281 Eulji-ro, Jung District, Seoul, Южная Корея	0101000020E61000007D16951E97C05F40632C2EE983C84240	t	82788d97-9e68-4975-9812-8d81bd71ce37	\N
d982c269-e55b-490b-812a-1f12be3fcebc	Insadong Street	Establishment, point of interest	Рейтинг Google: 4.3 (13504 отзывов). Адрес: Insa-dong, Jongno District, Seoul, Южная Корея	0101000020E61000006F319AF026BF5F40E7EC53443CC94240	f	82788d97-9e68-4975-9812-8d81bd71ce37	\N
84266444-3bff-4cda-900d-1ee812f3b25a	Lotte World	Amusement park, establishment	Рейтинг Google: 4.3 (48238 отзывов). Адрес: 240 Olympic-ro, Songpa District, Seoul, Южная Корея	0101000020E6100000F9A23D5E48C65F4004BC163E6CC14240	t	82788d97-9e68-4975-9812-8d81bd71ce37	\N
afea69ec-aad4-4177-9ff8-050e5b3f04ab	Changdeokgung Palace	Establishment, point of interest	Рейтинг Google: 4.6 (13559 отзывов). Адрес: 99 Yulgok-ro, Jongno District, Seoul, Южная Корея	0101000020E610000057FCF03D6DBF5F405BE5AECA2ACA4240	f	82788d97-9e68-4975-9812-8d81bd71ce37	\N
50bae29d-8b84-40d3-bdf7-aee13e10b6af	The War Memorial of Korea	Establishment, museum	Рейтинг Google: 4.6 (17920 отзывов). Адрес: 29 Itaewon-ro, Yongsan District, Seoul, Южная Корея	0101000020E6100000D8D7BAD488BE5F40B2F09AFCBBC44240	t	82788d97-9e68-4975-9812-8d81bd71ce37	\N
ec934808-aa58-40d9-ab59-42510e9c0109	Cheonggyecheon Stream	Establishment, park	Рейтинг Google: 4.5 (10458 отзывов). Адрес: Чонногу, Сеул, Южная Корея	0101000020E61000008FE62384A2BE5F40624D6551D8C84240	f	82788d97-9e68-4975-9812-8d81bd71ce37	\N
97bdb441-f6a2-4f17-acb6-a145969f7968	The Grand Palace	Establishment, park	Рейтинг Google: 4.6 (77177 отзывов). Адрес: Phra Borom Maha Ratchawang, Phra Nakhon, Bangkok 10200, Таиланд	0101000020E6100000DBBE47FD751F59408D6E7319ED7F2B40	f	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
98630f5e-5f18-4da2-ba67-dbd90bfd0bde	Wat Pho	Establishment, place of worship	Рейтинг Google: 4.7 (37088 отзывов). Адрес: 2 Thanon Sanam Chai, Khwaeng Phra Borom Maha Ratchawang, Khet Phra Nakhon, Krung Thep Maha Nakhon 10200, Таиланд	0101000020E6100000E3F50599891F59402BEB483F2B7E2B40	f	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
9e1079b6-071f-4b3a-b1ba-b1c3984524e5	Wat Arun	Establishment, place of worship	Рейтинг Google: 4.7 (43832 отзывов). Адрес: 158 Thanon Wang Doem, Khwaeng Wat Arun, Khet Bangkok Yai, Krung Thep Maha Nakhon 10600, Таиланд	0101000020E61000005B7B9FAA421F5940D74345E6DB7C2B40	f	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
9be94829-395d-41e9-b413-5145b2a6afe8	Chatuchak Weekend Market	Establishment, point of interest	Рейтинг Google: 4.4 (55053 отзывов). Адрес: 587, 10 Kamphaeng Phet 2 Rd, Khwaeng Chatuchak, Khet Chatuchak, Krung Thep Maha Nakhon 10900, Таиланд	0101000020E6100000B39AAE273A235940A2EC2DE57C992B40	f	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
ab8bc582-ff05-401c-802b-43e839256039	ICONSIAM	Establishment, point of interest	Рейтинг Google: 4.7 (56654 отзывов). Адрес: 299 Charoen Nakhon Rd, Khwaeng Khlong Ton Sai, Khet Khlong San, Krung Thep Maha Nakhon 10600, Таиланд	0101000020E61000005FECBDF8A2205940FA4DBC5EF5732B40	t	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
e384010b-0fb6-42b5-982d-5b3e9a4554c5	Jim Thompson House	Establishment, museum	Рейтинг Google: 4.5 (16754 отзывов). Адрес: 6 Soi Kasem San 2, Khwaeng Wang Mai, Pathum Wan, Krung Thep Maha Nakhon 10330, Таиланд	0101000020E6100000D2A00D65CD2159405B1025B5AB7F2B40	t	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
d70c09c5-627c-49ba-91c7-ff94672e5e51	Lumpini Park	Establishment, park	Рейтинг Google: 4.5 (39593 отзывов). Адрес: Лумпхини, Pathum Wan, Бангкок 10330, Таиланд	0101000020E6100000EA12C42FAB22594037C071BE7D762B40	f	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
0cef74e8-74b3-4d43-81dc-5dc4571002dc	Khao San Road	Route	Рейтинг Google: 4.1 (5049 отзывов). Адрес: Thanon Khao San, Khwaeng Talat Yot, Khet Phra Nakhon, Krung Thep Maha Nakhon 10200, Таиланд	0101000020E6100000942B6112D31F59407A85AA3D91842B40	f	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
ef187127-1531-46d2-8a76-f5e45fafd73c	Sea Life Ocean World	Aquarium, establishment	Рейтинг Google: 4.5 (28730 отзывов). Адрес: ชั้น บี1-บี2 สยามพารากอน 991 Rama I Rd, Khwaeng Pathum Wan, Pathum Wan, Krung Thep Maha Nakhon 10330, Таиланд	0101000020E6100000808868CF4022594082E09634EB7D2B40	t	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
198243e1-142a-4a27-b6dc-0d666db220a6	Wat Saket (Golden Mount)	Establishment, place of worship	Рейтинг Google: 4.7 (7679 отзывов). Адрес: 344 Thanon Chakkraphatdi Phong, Khwaeng Ban Bat, Khet Pom Prap Sattru Phai, Krung Thep Maha Nakhon 10100, Таиланд	0101000020E6100000E6CDE15A6D205940F3E093F36A812B40	f	8717ad74-80b9-4ac4-9640-bc1308ad3081	\N
f5ce0ae2-ebe6-476d-8b77-80edab6b2712	BONGENCOFFEE Ginza	Cafe, establishment	Рейтинг Google: 4.4 (1785 отзывов). Адрес: 2-chōme-16-3 Ginza, Chuo City, Tokyo 104-0061, Япония	0101000020E61000003E14BB6CAA786140616413AAE5D54140	f	7b2a2673-2a59-40aa-b097-c2b46a72c95f	\N
19e91f25-30e2-4b15-8941-5876823be2a6	Святилище Фусими Инари	Establishment, place of worship	Рейтинг Google: 4.6 (87025 отзывов). Адрес: 68 Fukakusa Yabunouchichō, Fushimi Ward, Kyoto, 612-0882, Япония	0101000020E61000005C6ED51AEFF860407102D369DD7B4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
b6343991-c9b7-49e6-917e-e702f3b5fe07	Киёмидзу-дэра	Establishment, place of worship	Рейтинг Google: 4.6 (68563 отзывов). Адрес: 1-chōme-294 Kiyomizu, Higashiyama Ward, Kyoto, 605-0862, Япония	0101000020E61000004BAE62F11BF96040E2B7D738517F4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
fb5eeb1d-fd68-4ad0-b757-331c5bbfb65d	Кинкаку-дзи	Establishment, place of worship	Рейтинг Google: 4.5 (67137 отзывов). Адрес: 1 Kinkakujichō, Kita Ward, Kyoto, 603-8361, Япония	0101000020E6100000AD2AA0F555F76040C5387F130A854140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
86d1d65d-3b1c-4427-84df-d3b85547afb6	Арашияма	Establishment, point of interest	Рейтинг Google: 4.5 (7167 отзывов). Адрес: Арасияма Генрокудзантё, Укё, Киото, 616-0007, Япония	0101000020E6100000639B543456F560406DFDF49F35814140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
c7a2756e-2885-4d84-9e49-61c22cd01929	Замок Нидзо	Establishment, point of interest	Рейтинг Google: 4.4 (41471 отзывов). Адрес: 541 Nijōjōchō, Nakagyo Ward, Kyoto, 604-8301, Япония	0101000020E610000072CFA91AF3F76040C7B370FECB814140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
a62e287e-1a16-45ec-aef7-fcae4a8c619d	Гинкаку-дзи	Establishment, place of worship	Рейтинг Google: 4.5 (17036 отзывов). Адрес: 2 Ginkakujichō, Sakyo Ward, Kyoto, 606-8402, Япония	0101000020E610000048CFE3E68AF96040D0E5176F75834140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
fdfd3cda-a765-4f18-b418-867e2fae0277	Эйкан-до	Establishment, place of worship	Рейтинг Google: 4.6 (9494 отзывов). Адрес: 48 Eikandōchō, Sakyo Ward, Kyoto, 606-8445, Япония	0101000020E6100000943AB7BF69F960403D5AE6BEE6814140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
812c6cf4-9350-4597-8b30-8e37cbd41a01	Nishiki Market	Establishment, point of interest	Рейтинг Google: 4.3 (51116 отзывов). Адрес: Higashiuoyacho, Nakagyo Ward, Kyoto, 604-8055, Япония	0101000020E6100000F86F5E9C78F86040705177AFA4804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
330a5f8a-732e-497b-b883-8ccef91ff08e	То-дзи	Establishment, place of worship	Рейтинг Google: 4.5 (19298 отзывов). Адрес: 1 Kujōchō, Minami Ward, Kyoto, 601-8473, Япония	0101000020E6100000D13DEB1AEDF760400EBDC5C37B7D4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
95b69dfc-71a2-4e85-9f37-a98cfb2f54f4	Рёан-дзи	Establishment, place of worship	Рейтинг Google: 4.5 (11028 отзывов). Адрес: 13 Ryōanji Goryōnoshitachō, Ukyo Ward, Kyoto, 616-8001, Япония	0101000020E61000003E9D8603FCF66040FF32294F6A844140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
00e387f7-e937-4ef2-9a78-8feaed08f869	Киотский ботанический сад	Establishment, point of interest	Рейтинг Google: 4.4 (7316 отзывов). Адрес: Симогамо Хангитё, Sakyo Ward, Киото, 606-0823, Япония	0101000020E610000094933FCE6AF86040F502A21639864140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
9fee94ed-b007-44a4-8cfb-836ecd4ab611	Тофуку-дзи	Establishment, place of worship	Рейтинг Google: 4.5 (10994 отзывов). Адрес: 15-chōme-778 Honmachi, Higashiyama Ward, Kyoto, 605-0981, Япония	0101000020E6100000AB6BFEA9C2F86040098A1F63EE7C4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
b16e2e31-078b-402c-a72a-13fed4cc9580	Ясака-дзиндзя	Establishment, place of worship	Рейтинг Google: 4.4 (32410 отзывов). Адрес: 625 Gionmachi Kitagawa, Higashiyama Ward, Kyoto, 605-0073, Япония	0101000020E610000011E6D1E8E9F86040FE77E9CB77804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
d943defa-ecf8-4b8d-adfc-b31f633ee3b2	Arashiyama Bamboo Forest	Establishment, park	Рейтинг Google: 4.3 (21813 отзывов). Адрес: Сагаогураяма Табутияматё, Укё, Киото, 616-8394, Япония	0101000020E61000006528DD4C7BF560400A3B7B1D27824140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
9f53d2aa-22de-406d-a1b3-54d29ccd5251	Симогамо	Establishment, place of worship	Рейтинг Google: 4.5 (14940 отзывов). Адрес: Япония, 〒606-0807 京都府京都市左京区下鴨泉川町５９	0101000020E6100000BDB2C178BCF8604090227C39FD844140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
7d126114-2d1f-4cf3-b828-e7caca8593b8	Kennin-ji Temple	Establishment, place of worship	Рейтинг Google: 4.5 (9289 отзывов). Адрес: ５８４番地 Komatsuchō, Higashiyama Ward, Kyoto, 605-0811, Япония	0101000020E610000074AC9C07C1F860400BA8813001804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
f44117b1-dd06-4f10-a11b-b7da4966582d	Sannenzaka	Establishment, point of interest	Рейтинг Google: 4.4 (16284 отзывов). Адрес: 2-chōme-211 Kiyomizu, Higashiyama Ward, Kyoto, 605-0862, Япония	0101000020E6100000433D7D04FEF86040328BF5B2927F4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
a8e9c79d-1efc-4a01-a6a7-4b9e4629f6a4	Kyoto Sento Imperial Palace	Establishment, point of interest	Рейтинг Google: 4.4 (1602 отзывов). Адрес: Кётогёэн, Kamigyo Ward, Киото, 602-0881, Япония	0101000020E61000008871EDFA7BF86040ADF2A908DC824140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
29ca3418-6a20-4c60-8025-46c10da9b197	Храм Хэйан	Establishment, place of worship	Рейтинг Google: 4.4 (15755 отзывов). Адрес: 97 Okazaki Nishitennōchō, Sakyo Ward, Kyoto, 606-8341, Япония	0101000020E6100000F840E1A209F960404DE83FB50B824140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
a272d73c-c9e4-475d-acd0-396f0ab932cf	SAMURAI NINJA MUSEUM Kyoto	Establishment, museum	Рейтинг Google: 4.8 (22306 отзывов). Адрес: 109 Horinouechō, Nakagyo Ward, Kyoto, 604-8117, Япония	0101000020E610000071B9B0246FF86040163E117AEC804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
a768f3b6-49d5-49d4-9279-93d2b14cbeaa	Shōseien Garden	Establishment, point of interest	Рейтинг Google: 4.2 (2823 отзывов). Адрес: Япония, 〒600-8190 Kyoto, Shimogyo Ward, Higashitamamizuchō, 下珠数屋町通間之町東入東玉水町	0101000020E6100000255987A36BF860407FDF1A33E47E4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
0b7018ae-65bf-4576-bbe8-a82515fc6f7a	Сад камней	Establishment, point of interest	Рейтинг Google: 4.5 (411 отзывов). Адрес: 13-1 Ryōanji Goryōnoshitachō, Ukyo Ward, Kyoto, 616-8001, Япония	0101000020E61000005C15F252FBF66040AD403E3267844140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
da893f46-74ad-4cb5-9c20-a75ad0492948	Парк обезьян Арасияма Иватаяма	Amusement park, establishment	Рейтинг Google: 4.5 (13915 отзывов). Адрес: Япония, 〒616-0004 Kyoto, Nishikyo Ward, Arashiyama Nakaoshitachō, ６１−６１	0101000020E610000084656CE8A6F56040412B306475814140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
ed38f9b7-d5b5-465f-b26e-0884a807e35e	Окочи Сансо	Establishment, point of interest	Рейтинг Google: 4.6 (1833 отзывов). Адрес: 8 Sagaogurayama Tabuchiyamacho, Ukyo Ward, Kyoto, 616-8394, Япония	0101000020E610000023EBBA0170F5604065EE10B523824140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
94470418-85e5-42b2-aec9-a2b2d1eb7cae	Сайходзи	Establishment, place of worship	Рейтинг Google: 4.5 (1899 отзывов). Адрес: 56 Matsuojingatanichō, Nishikyo Ward, Kyoto, 615-8286, Япония	0101000020E6100000074E6CF4E0F5604006A9CAADFF7E4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
e1283d62-48e7-43d9-97ee-f4189be7d964	Kacto	Establishment, food	Рейтинг Google: 4.5 (1213 отзывов). Адрес: 133 Saitōchō, Shimogyo Ward, Kyoto, 600-8012, Япония	0101000020E6100000AA0194D0A7F86040F89C05EB49804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
cb58daad-c860-4a94-9bcd-dc5b2c6ca6df	Itoh Dining	Establishment, food	Рейтинг Google: 4.6 (928 отзывов). Адрес: Япония, 〒605-0085 Kyoto, Higashiyama Ward, Sueyoshichō, ８０	0101000020E6100000E23B31EBC5F86040FDB73764A8804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
6f4769a2-af28-4412-83b8-e2f2dc03724f	GYUKATSU Kyoto Katsugyu Kiyomizu Gojozaka	Establishment, food	Рейтинг Google: 4.8 (12650 отзывов). Адрес: 6-chōme-583 Gojōbashihigashi, Higashiyama Ward, Kyoto, 605-0846, Япония	0101000020E6100000D0C1E913EFF860401A34F44F707F4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
d9a088c0-a8b7-483f-bd7f-ebc03222ef55	MOKO	Establishment, food	Рейтинг Google: 4.9 (132 отзывов). Адрес: 235-2 Tamauechō, Nakagyo Ward, Kyoto, 604-0005, Япония	0101000020E6100000B224E5933AF860407A4C497B28824140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
0bfb1c39-01ce-483c-bfb1-f68d2f26ba59	Arashiyama Itsukichaya	Establishment, food	Рейтинг Google: 4.6 (2957 отзывов). Адрес: Япония, 〒616-8383 Kyoto, Ukyo Ward, Saganakanoshimachō, 官有地10	0101000020E6100000033972EEC0F56040F4E791F58A814140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
13ef7097-a467-4f1e-a595-fdc4f36fc64a	Sugarhill Kyoto	Establishment, food	Рейтинг Google: 4.7 (945 отзывов). Адрес: 725 Uematsuchō, Shimogyo Ward, Kyoto, 600-8028, Япония	0101000020E6100000AFCDC64A8CF86040D2C20A5CC37F4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
c1f1d546-6979-4a35-b28b-d7c18167627d	Teppanyaki Manryu	Establishment, food	Рейтинг Google: 4.7 (741 отзывов). Адрес: Япония, 〒605-0083 Kyoto, Higashiyama Ward, Hashimotochō, 2丁目３８２−２ 1F	0101000020E6100000E1421EC1CDF86040E89903A9B9804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
6d9930ba-0712-4cda-a326-763dd055cc96	Teppan Tavern Tenamonya	Bar, establishment	Рейтинг Google: 4.8 (678 отзывов). Адрес: Япония, 〒605-0074 Kyoto, Higashiyama Ward, Gionmachi Minamigawa, ５３７−２ B1F	0101000020E6100000B1755F84DFF8604093C9A99D61804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
9bc83453-eddd-4d0a-9e98-706e8790112d	Wagyu Ryotei Bungo Gion	Establishment, food	Рейтинг Google: 4.7 (882 отзывов). Адрес: 56 Motoyoshichō, Higashiyama Ward, Kyoto, 605-0087, Япония	0101000020E61000005CF05822C6F860409F65CC13BE804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
c85a21ce-f513-472f-a396-de5c16c1d28d	Sushi Naritaya	Establishment, food	Рейтинг Google: 4.8 (1287 отзывов). Адрес: Япония, 〒616-8385 Kyoto, Ukyo Ward, Sagatenryūji Susukinobabachō, 嵯峨天龍寺芒ノ馬場25嵐山スクエアウエストパ―ク	0101000020E610000064856C6AAAF560404ED60341DB814140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
205f3c86-6d16-47e9-a723-3f37e60d4beb	Katsu	Establishment, food	Рейтинг Google: 4.9 (1263 отзывов). Адрес: 1-4 Ryōanji Saigūchō, Ukyo Ward, Kyoto, 616-8011, Япония	0101000020E6100000B4C6455A0FF76040FF6ECB91DF834140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
788870e9-f0da-4e00-a3a0-e5131fe8e9a1	Kijurou	Establishment, food	Рейтинг Google: 4.5 (1659 отзывов). Адрес: 18-27 Sagatenryūji Kitatsukurimichichō, Ukyo Ward, Kyoto, 616-8374, Япония	0101000020E6100000D1DE2A99ADF5604069290FC127824140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
e2fd41d0-f6d9-4e58-acf5-a62e984b7091	LURRA°	Establishment, food	Рейтинг Google: 4.4 (226 отзывов). Адрес: 396 Sekiseninchō, Higashiyama Ward, Kyoto, 605-0021, Япония	0101000020E6100000BBC106FAFAF86040ABD1AB014A814140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
d6401202-64ff-4feb-a012-4fc289c9174f	IMAYA Kyoto &COFFEE	Cafe, establishment	Рейтинг Google: 4.8 (1162 отзывов). Адрес: 726-4 Shimomatsuyachō, Nakagyo Ward, Kyoto, 604-0034, Япония	0101000020E6100000B5125F922FF86040F82A436678814140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
2453150e-db44-41af-9bbd-9ff94b63736f	Tempura Endo Yasaka (North)	Establishment, food	Рейтинг Google: 4.4 (1880 отзывов). Адрес: 566 Komatsuchō, Higashiyama Ward, Kyoto, 605-0811, Япония	0101000020E61000001D16B4DACDF8604065DE4F32DE7F4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
6d294e6b-66dd-4825-9d88-a5beaaceefd1	THE SODOH HIGASHIYAMA KYOTO	Establishment, food	Рейтинг Google: 4.3 (2046 отзывов). Адрес: 366 Yasaka Kamimachi, Higashiyama Ward, Kyoto, 605-0827, Япония	0101000020E6100000D6BF907AF4F86040447FB273E47F4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
f60a9ee5-730e-4907-a174-54e9744c827b	Burger Revolution Kyoto	Establishment, food	Рейтинг Google: 4.5 (2173 отзывов). Адрес: 586 Myōmanjichō, Shimogyo Ward, Kyoto, 600-8392, Япония	0101000020E6100000A0B250210DF86040F5CCDC8D4F804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
b2c53bce-058c-4c0d-94a0-d957d2d6d4a9	Kikyo Sushi	Establishment, food	Рейтинг Google: 4.7 (1681 отзывов). Адрес: 43 Daimonjichō, Nakagyo Ward, Kyoto, 604-0071, Япония	0101000020E610000033CB54771BF860404CDD955D30824140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
96ecd483-5576-4241-ab26-2ccb417465d4	Kikunoi Honten	Establishment, food	Рейтинг Google: 4.4 (931 отзывов). Адрес: 459 Shimokawarachō, Higashiyama Ward, Kyoto, 605-0825, Япония	0101000020E61000004A54B99A06F96040CF5F8D5830804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
cb51b8eb-5e35-41fe-af09-20a16485e838	Kyoto Gyoen National Garden	Establishment, park	Рейтинг Google: 4.5 (9642 отзывов). Адрес: 3 Kyōtogyoen, Kamigyo Ward, Kyoto, 602-0881, Япония	0101000020E610000039C9A0246EF8604024A58FAFF3824140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
fba93840-40a5-4dfa-a51f-18f69123d3a5	Arashiyama Park Nakanoshima Area	Establishment, park	Рейтинг Google: 4.4 (4214 отзывов). Адрес: Саганаканосиматё, Укё, Киото, 616-8383, Япония	0101000020E6100000C950BA99B6F56040BFE83C748B814140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
f0897121-513b-4c0b-b6f4-460ba4eb900d	Парк Маруяма	Establishment, park	Рейтинг Google: 4.3 (6775 отзывов). Адрес: Маруяматё, Higashiyama Ward, Киото, 605-0071, Япония	0101000020E6100000BFA48C13FAF86040E20E8A9C74804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
bf8ed23a-7391-4b21-bdf3-23020a64af0f	Arashiyama Park Kameyama Area	Establishment, park	Рейтинг Google: 4.5 (1272 отзывов). Адрес: Япония, 〒616-8386 京都府京都市右京区嵯峨亀ノ尾町６	0101000020E6100000ED0BE8857BF56040DED0EF56F1814140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
4ef37b3e-5427-470f-bdd3-af9fdbabba8a	Umekōji Park	Establishment, museum	Рейтинг Google: 4.2 (10116 отзывов). Адрес: 56-3 Kankijichō, Shimogyo Ward, Kyoto, 600-8836, Япония	0101000020E6100000F2892B1DE2F760406ED85B6F407E4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
6bdcb88f-93ed-4788-b77b-28416e1b4c2a	Katsuragawa Wild Bird Park	Establishment, park	Рейтинг Google: 3.8 (147 отзывов). Адрес: 1-100 Goryōkitaōeyamachō, Nishikyo Ward, Kyoto, 610-1107, Япония	0101000020E6100000082D358C4CF56040ACAE9EEE977E4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
ccdfba23-b291-4525-a68c-926d6a044c63	Pontocho Park	Establishment, park	Рейтинг Google: 4.4 (1014 отзывов). Адрес: 先斗町通, １４５, Umenokichō, Nakagyo Ward, Kyoto, 604-8012, Япония	0101000020E6100000A7A498CDADF86040EEA4749FD2804140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
17594a72-d8c4-427b-abe0-00979d30ba03	Katsurazaka Park	Establishment, park	Рейтинг Google: 4 (263 отзывов). Адрес: 4-chōme-9 Goryōōeyamachō, Nishikyo Ward, Kyoto, 610-1102, Япония	0101000020E6100000F6C07DD36AF560409FCDAACFD57D4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
740acc56-ca30-4fdf-8c65-ae474e673321	Katsura Imperial Villa	Establishment, point of interest	Рейтинг Google: 4.5 (2495 отзывов). Адрес: Кацурамисоно, Nishikyo Ward, Киото, 615-8014, Япония	0101000020E610000009C556D0B4F660407847C66AF37D4140	f	5b3d3373-40ad-49d9-b7b9-27c8214e5a7e	\N
c636c631-cb1a-479a-bd85-fcc4eb905f72	Улица Дотонбори	Establishment, point of interest	Рейтинг Google: 4.4 (82837 отзывов). Адрес: 1 Тёме-9 Дотомбори, Chuo Ward, Осака, 542-0071, Япония	0101000020E61000008C4237A00AF06040F38876BA98554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
2cd8a79f-986f-4adb-9f28-3f870675152e	Замок в Осаке	Establishment, museum	Рейтинг Google: 4.4 (94509 отзывов). Адрес: 1-1 Ōsakajō, Chuo Ward, Osaka, 540-0002, Япония	0101000020E610000070AE06CDD3F06040CE38680AF8574140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
c9d00280-adb1-4411-b789-73bcf3d98cf1	Цутэнкаку	Establishment, landmark	Рейтинг Google: 4.1 (41318 отзывов). Адрес: 1-chōme-18-6 Ebisuhigashi, Naniwa Ward, Osaka, 556-0002, Япония	0101000020E6100000CE9838A833F060404555021885534140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
16b50557-5ee2-4889-af1c-6ba2369e4bd6	Umeda Sky Building	Establishment, point of interest	Рейтинг Google: 4.4 (41060 отзывов). Адрес: 1-chōme-1-88 Ōyodonaka, Kita Ward, Osaka, 531-6023, Япония	0101000020E6100000BD9C233CABEF6040CA24D9D9465A4140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
6c0685fe-7973-43ed-87e2-6cd9c5531c9e	Аквариум Каюкан	Aquarium, establishment	Рейтинг Google: 4.5 (57764 отзывов). Адрес: 1-chōme-1-10 Kaigandōri, Minato Ward, Osaka, 552-0022, Япония	0101000020E6100000A454C213BAED604082D19B40C7534140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
7c71a915-b861-493f-884c-6a75275b5594	Shinsaibashi-Suji Shopping Street	Establishment, point of interest	Рейтинг Google: 4.3 (20693 отзывов). Адрес: 2-chōme-2-22 Shinsaibashisuji, Chuo Ward, Osaka, 542-0085, Япония	0101000020E61000004E75125B0BF06040ACB827FEDE554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
396cd8b3-1e1b-444f-9783-88c4cd5f145c	Harukas 300	Establishment, point of interest	Рейтинг Google: 4.6 (22088 отзывов). Адрес: 1-chōme-1-43 Abenosuji, Abeno Ward, Osaka, 545-6016, Япония	0101000020E6100000A7A734076DF06040DC195C29BA524140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
96c2826e-bd8c-4d5d-9dc4-73da8406cfd7	Nakanoshima Park	Establishment, park	Рейтинг Google: 4.2 (6284 отзывов). Адрес: 1 Chome-1 Nakanoshima, Kita Ward, Osaka, 530-0005, Япония	0101000020E610000047B071FD3BF060404177EEE2A2584140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
e3d5a516-cd26-444b-a26b-d7d9e84cc019	Абено Харукас	Establishment, point of interest	Рейтинг Google: 4.2 (53062 отзывов). Адрес: 1-chōme-1-43 Abenosuji, Abeno Ward, Osaka, 545-6016, Япония	0101000020E6100000D6F786676EF060401CF40071B2524140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
ac365f68-3c86-4115-a6df-f350ad26e4e3	Парк студии "Юниверсал" в Осаке	Amusement park, establishment	Рейтинг Google: 4.5 (150811 отзывов). Адрес: 2-chōme-1-33 Sakurajima, Konohana Ward, Osaka, 554-0031, Япония	0101000020E6100000965E9B8DD5ED60405CDABAE534554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
77e6d219-7636-496f-87f8-23956012ff20	Tempozan Ferris Wheel	Establishment, point of interest	Рейтинг Google: 4.5 (10481 отзывов). Адрес: 1-chōme-1-10 Kaigandōri, Minato Ward, Osaka, 552-0022, Япония	0101000020E61000001EC6FF78CAED60402332079C00544140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
ed4f7999-7d52-44cf-b53e-bb2652a50713	Kuchu Teien Observatory	Establishment, point of interest	Рейтинг Google: 4.4 (13809 отзывов). Адрес: Япония, 〒531-6039 Osaka, Kita Ward, Ōyodonaka, 1-chōme−1−８８ 梅田スカイビル	0101000020E610000020DA22C4B0EF60409EEFA7C64B5A4140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
916174aa-a734-4ba3-a356-a7e06eee995b	Osaka Science Museum	Establishment, museum	Рейтинг Google: 4.2 (4042 отзывов). Адрес: 4-chōme-2-1 Nakanoshima, Kita Ward, Osaka, 530-0005, Япония	0101000020E61000003BF1E6BABAEF60402D0ABB287A584140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
a678d7bb-5e45-4e8d-9a32-c0916f64d433	Ōte-mon Gate	Establishment, point of interest	Рейтинг Google: 4.4 (721 отзывов). Адрес: 2-2 Ōsakajō, Chuo Ward, Osaka, 540-0002, Япония	0101000020E61000004CB2C4B9BCF0604082638511B1574140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
244f51b4-eaf2-4e9c-805c-7a30d679b7a9	Kuromon Market	Establishment, point of interest	Рейтинг Google: 4.1 (20175 отзывов). Адрес: 2 Chome-21 Nipponbashi, Chuo Ward, Osaka, 542-0073, Япония	0101000020E61000000A9D7C1F33F060403EE6A8482A554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
1d597990-d67f-4804-a5bc-3925b2bf91d8	Hep Five Ferris wheel	Establishment, point of interest	Рейтинг Google: 4.4 (6756 отзывов). Адрес: Япония, 〒530-0017 Osaka, Kita Ward, Kakudachō, 5−１５ HEP FIVE 7F	0101000020E61000007100FDBEFFEF604054F6A79E165A4140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
ac4e0a0a-0ddc-497f-9338-de4093c72fef	Зоопарк Тэннодзи	Establishment, park	Рейтинг Google: 4.1 (17119 отзывов). Адрес: 1-108 Chausuyamachō, Tennoji Ward, Osaka, 543-0063, Япония	0101000020E61000002A05381845F060407A08991A57534140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
d2d1c8d2-18cd-4765-b3a8-22b94f5bd063	Minion Park	Amusement park, establishment	Рейтинг Google: 4.5 (146 отзывов). Адрес: 2-chōme-1-5 Sakurajima, Konohana Ward, Osaka, 554-0031, Япония	0101000020E6100000FDE95097D6ED6040413FF8F5E8544140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
04327352-ab25-4e74-bc8b-e9ce15436297	Тэннодзи	Establishment, park	Рейтинг Google: 4.1 (8777 отзывов). Адрес: 5-55 Chausuyamachō, Tennoji Ward, Osaka, 543-0063, Япония	0101000020E61000004E3C0C5255F060401B5943F34A534140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
90a0105b-1965-4368-8d0d-6e850975513b	Universal Wonderland	Amusement park, establishment	Рейтинг Google: 4.4 (375 отзывов). Адрес: Япония, 〒554-0031 Osaka, Konohana Ward, Sakurajima, 2-chōme−1−３３ ユニバーサル・スタジオ・ジャパン	0101000020E610000080931227DCED6040E66BE05861554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
eb7f1d85-0601-494d-b061-0e251eb410f5	American Village	Establishment, point of interest	Рейтинг Google: 3.9 (2769 отзывов). Адрес: 2 Chome-11 Nishishinsaibashi, Chuo Ward, Osaka, 542-0086, Япония	0101000020E61000004194D4AEEEEF60406011B2E20A564140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
5c9ae304-7231-4f0e-b2ab-11608672b9df	Hogwarts™ Castle Walk	Amusement park, establishment	Рейтинг Google: 4.5 (29 отзывов). Адрес: 2-chōme-1-1 Sakurajima, Konohana Ward, Osaka, 554-0031, Япония	0101000020E61000003F598C15D0ED6040DA5FD10891554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
ee88b3fd-17fc-4543-98d9-7530efacf221	Nishinomaru Garden	Establishment, point of interest	Рейтинг Google: 4.2 (2331 отзывов). Адрес: 2-2 Ōsakajō, Chuo Ward, Osaka, 540-0002, Япония	0101000020E6100000A1F7C610C0F060403C82C06FE8574140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
86cbad30-afab-48c2-ac6b-f10498b5f8e3	Хозендзи Храм	Establishment, place of worship	Рейтинг Google: 4.4 (4297 отзывов). Адрес: 1-chōme-2-16 Namba, Chuo Ward, Osaka, 542-0076, Япония	0101000020E610000096A9EE3614F060403059260D7F554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
1d8af946-fc32-44dd-85f9-97470976967e	The Wizarding World Of Harry Potter	Amusement park, establishment	Рейтинг Google: 4.7 (2858 отзывов). Адрес: 2 Chome-1 Sakurajima, Konohana Ward, Osaka, 554-0031, Япония	0101000020E610000092CA1473D0ED6040CF166B1382554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
5b2c7584-597d-4edc-a0cb-edf991cd3468	Hozenji Yokocho	Establishment, point of interest	Рейтинг Google: 4.3 (463 отзывов). Адрес: 1-chōme-1-17 Namba, Chuo Ward, Osaka, 542-0076, Япония	0101000020E610000025D4676215F060404B2CDFE984554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
cd44db69-5fed-4622-9bae-ff0c9634d4f0	Harry Potter and the Forbidden Journey™	Establishment, point of interest	Рейтинг Google: 4.6 (1348 отзывов). Адрес: 2-chōme-1-33 Sakurajima, Konohana Ward, Osaka, 554-0031, Япония	0101000020E61000004E6ECACBD0ED6040A11A8A9697554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
42555d7a-42db-41da-a0bc-0ae3d0f220de	Kobe Beef WANOMIYA Dotonbori Main Store	Establishment, food	Рейтинг Google: 4.8 (4004 отзывов). Адрес: 1-chōme-5-2 Dōtonbori, Chuo Ward, Osaka, 542-0071, Япония	0101000020E61000009841C6ED21F06040E0F76F5E9C554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
679e37f0-5775-4bbf-ad69-21eecc9913fc	Chitose	Establishment, food	Рейтинг Google: 4.7 (1747 отзывов). Адрес: 1-chōme-11-10 Taishi, Nishinari Ward, Osaka, 557-0002, Япония	0101000020E6100000379DAE3826F06040D42B6519E2524140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
e0348a86-c9f9-462a-9a2d-31c9845ab633	Kuma Kafe	Cafe, establishment	Рейтинг Google: 4.8 (655 отзывов). Адрес: 4-chōme-4-15 Chikkō, Minato Ward, Osaka, 552-0021, Япония	0101000020E6100000EF3DB72BCFED6040A1191FC1E8534140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
6dc19b9e-6642-4752-8c4c-5060e6514499	Wagyu IDATEN	Establishment, food	Рейтинг Google: 4.6 (1104 отзывов). Адрес: Япония, 〒542-0076 Osaka, Chuo Ward, Namba, 1-chōme−8−２０ 嘉光ビル 2階	0101000020E61000005510A8A308F060401B8B5C2679554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
5a42bb32-47b1-418d-95a0-cee107489528	Alto Tritone	Establishment, food	Рейтинг Google: 4.6 (291 отзывов). Адрес: Япония, 〒531-0075 Osaka, Kita Ward, Ōyodominami, 1-chōme−4−２０ 長谷川ビル 1階	0101000020E6100000CB660E49ADEF6040E35AA3D4145A4140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
78d684c5-08f9-499b-be71-ef7095bc921a	Москва Плюс Семь	Establishment, food	Рейтинг Google: 4.2 (323 отзывов). Адрес: Япония, 〒530-0001 Osaka, Kita Ward, Umeda, 1-chōme−3−１ 大阪駅前第一ビル 地下1階	0101000020E610000021C9ACDEE1EF6040B0027CB779594140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
e3ae5bb7-a429-47b1-b71c-a52aed4468c9	Shabu-shabu & Sukiyaki & Sushi Restaurant :Niku-no-Asatsu Umeda Ohatsu Tenjin	Establishment, food	Рейтинг Google: 4.7 (3229 отзывов). Адрес: Япония, 〒530-0057 Osaka, Kita Ward, Sonezaki, 2-chōme−5−２０ お初天神ビル 3F	0101000020E61000009D972FD406F060403DCED9A788594140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
c08c0e54-bee5-4c7e-9eba-1ce4506381bd	Maidreamin Osaka Namba Store	Cafe, establishment	Рейтинг Google: 4.9 (9977 отзывов). Адрес: Япония, 〒556-0011 Osaka, Naniwa Ward, Nanbanaka, 2-chōme−2−２１ 3F	0101000020E61000001A7A7A5B1FF06040883E69F2DE544140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
f69ba202-3c60-4a1d-8976-8b2e3cc08245	寿司直	Establishment, food	Рейтинг Google: 5 (2 отзывов). Адрес: 2-chōme-7-3 Uchikyūhōjimachi, Chuo Ward, Osaka, 540-0013, Япония	0101000020E6100000CD6960F591F06040F46A2519DE564140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
8a32588e-b94a-4c40-bb7e-1b25b15a991d	Micasadeco & Cafe	Cafe, establishment	Рейтинг Google: 4.1 (1464 отзывов). Адрес: 1-chōme-2-8 Saiwaichō, Naniwa Ward, Osaka, 556-0021, Япония	0101000020E6100000C484871FD2EF6040A730A5E48B554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
8d2e7b04-7384-4ead-82fa-5056dd20ba2f	Pokémon Cafe Osaka Shinsaibashi	Cafe, establishment	Рейтинг Google: 4.1 (1299 отзывов). Адрес: 1-chōme-7-1 Shinsaibashisuji, Chuo Ward, Osaka, 542-8501, Япония	0101000020E61000001A8B016D06F06040C42DD5BB2E564140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
c11d16e0-87ba-4da3-aa12-508bbd539c3b	Pierre	Establishment, food	Рейтинг Google: 4.5 (252 отзывов). Адрес: インターコンチネンタルホテル大阪, 20F, 3-60 Ōfukachō, Kita Ward, Osaka, 530-0011, Япония	0101000020E6100000AE8F98EAD3EF6040F24AEDA06D5A4140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
8fd03648-9edb-4a2a-851f-d54caf09fbc8	KAHALA	Establishment, food	Рейтинг Google: 4.7 (43 отзывов). Адрес: Япония, 〒530-0002 Osaka, Kita Ward, Sonezakishinchi, 1-chōme−9−２ 2F	0101000020E610000046933078FDEF60400BB20A4048594140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
37d22adc-5d47-4e10-8939-8c5579c1b65d	Taishu Sukiyaki Hokuto GEMS Namba Branch	Establishment, food	Рейтинг Google: 4.7 (1791 отзывов). Адрес: １９GEMSなんば, 7F, 3-chōme-7-7 Namba, Chuo Ward, Osaka, 542-0076, Япония	0101000020E61000001E85909805F06040893B832B45554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
00f28960-5f6b-4233-90ed-9fc728e84285	Arigato Kitchen Seafood Izakaya	Establishment, food	Рейтинг Google: 4.8 (87 отзывов). Адрес: Япония, 〒542-0076 Osaka, Chuo Ward, Namba, 3-chōme−1−３２ 2階	0101000020E61000003B736AC211F0604082A0EDE247554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
2d054df5-70d9-421a-9c4a-fa101f0f6abd	Hajime	Establishment, food	Рейтинг Google: 4.4 (291 отзывов). Адрес: Япония, 〒550-0002 Osaka, Nishi Ward, Edobori, 1-chōme−9−１１ アイ・プラス江戸堀 １F	0101000020E61000000BBEC4B3DFEF604069290FC127584140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
71c303b5-a59a-4679-8909-833ed7adcbc5	Kani Doraku Dotonbori Main Branch	Establishment, food	Рейтинг Google: 4.2 (4924 отзывов). Адрес: 1-chōme-6-18 Dōtonbori, Chuo Ward, Osaka, 542-0071, Япония	0101000020E6100000801B182F0CF060403A8B28379B554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
bcc42067-dcf6-4ae6-8c16-6a60c2b9069b	Tonkatsu Fujii	Establishment, food	Рейтинг Google: 4.8 (214 отзывов). Адрес: 1-chōme-11-5 Senbayashi, Asahi-ku, Osaka, 535-0012, Япония	0101000020E6100000EA9B8FC6BCF16040BE1CD198A45C4140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
328d3b82-6805-4b45-8d70-40faa37e6d98	Brooklyn Roasting Company Namba	Cafe, establishment	Рейтинг Google: 4.4 (1545 отзывов). Адрес: 1-chōme-1-21 Shikitsuhigashi, Naniwa Ward, Osaka, 556-0012, Япония	0101000020E6100000C8073D9B15F06040AB3FC23060544140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
e3477300-4ead-40a0-9c1f-7afe00a85f6a	Table36	Establishment, food	Рейтинг Google: 4.2 (668 отзывов). Адрес: スイスホテル南海大阪36階, 中央区, ５丁目-１-60 難波 中央区 大阪市 大阪府 542-0076, Япония	0101000020E6100000A8959DD909F0604026F103A106554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
f5520d63-8c5f-4c30-854c-c5851440ed55	Nagai Park	Establishment, park	Рейтинг Google: 4.2 (8778 отзывов). Адрес: 1-1 Nagaikōen, Higashisumiyoshi Ward, Osaka, 546-0034, Япония	0101000020E61000009797B2C2A3F0604018A941E2684E4140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
af53bea3-820a-4201-b41d-cd707da25eda	Minoh Park	Establishment, park	Рейтинг Google: 4.5 (2507 отзывов). Адрес: 1-18 Minookōen, Minoh, Osaka 562-0002, Япония	0101000020E6100000448C32761DEF6040993336CF6C6C4140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
b33766bf-7cb5-48d4-80d2-9cbbde89ec9c	Kema Sakuranomiya Park	Establishment, park	Рейтинг Google: 4.2 (2574 отзывов). Адрес: 5 Chome-12 Nakanocho, Miyakojima Ward, Osaka, 534-0027, Япония	0101000020E61000007017505E9AF06040C65FA461425A4140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
7542f470-b998-4332-a292-678a74afdbdf	Tsurumi Ryokuchi Park	Establishment, park	Рейтинг Google: 4.2 (7686 отзывов). Адрес: 2-163 Ryokuchikōen, Tsurumi Ward, Osaka, 538-0036, Япония	0101000020E61000003F8B4A8F4BF26040BC1BB050105B4140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
fd3810c1-9301-4047-8e10-f5bb271c527d	Osaka Castle Park	Establishment, park	Рейтинг Google: 4.4 (50119 отзывов). Адрес: Осакадзё, Chuo Ward, Осака, 540-0002, Япония	0101000020E610000009394AB9D6F06040176F1A91DE574140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
b359118a-2538-4bd7-af41-a8e95e26cf27	Osaka Maishima Seaside Park	Establishment, point of interest	Рейтинг Google: 4.1 (793 отзывов). Адрес: 2 Chome-1 Hokkoryokuchi, Konohana Ward, Osaka, 554-0042, Япония	0101000020E61000005EE62ACC71EC604049E5DCDC4E554140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
4a96e6d8-c896-4b74-9a2b-5e70aea70db6	Парк Уцубо	Establishment, park	Рейтинг Google: 4.1 (4599 отзывов). Адрес: 1 Chome-9 Utsubohonmachi, Nishi Ward, Osaka, 550-0004, Япония	0101000020E6100000D75BB9CDCAEF6040A12C7C7DAD574140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
623d31c1-79bc-4885-9d73-0e7b8c824f8f	Oizumi Ryokuchi Park	Establishment, park	Рейтинг Google: 4.2 (3650 отзывов). Адрес: 128 Kanaokachō, Kita Ward, Sakai, Osaka 591-8022, Япония	0101000020E61000006317FB81E1F06040F676F0B84D484140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
a6160b16-afe0-4548-a40b-208cdc0202ee	Osaka Park	Establishment, park	Рейтинг Google: 3.4 (10 отзывов). Адрес: 1-chōme-3-15 Ōsaka, Tennoji Ward, Osaka, 543-0062, Япония	0101000020E6100000D54B42D85FF06040EE3C96E3BA534140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
f8ea4383-db2c-4a43-b902-ea319bd53877	Сад Кейтакуэн	Establishment, point of interest	Рейтинг Google: 4.3 (800 отзывов). Адрес: Япония, 〒543-0063 Osaka, Tennoji Ward, Chausuyamachō, 1−１ 天王寺公園 内	0101000020E6100000A68526E45EF060409E0EBFF627534140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
862a1ffc-11f8-4d2b-b6a0-411b9e11de20	Hoshida Park	Establishment, park	Рейтинг Google: 4.3 (614 отзывов). Адрес: 5019-1 Hoshida, Katano, Osaka 576-0011, Япония	0101000020E6100000721AFDC3F1F560404656236019604140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
3a87007b-9aee-4718-a95f-e5669d5e8c07	Sennan Rinkū Park (Sennan Long Park)	Establishment, park	Рейтинг Google: 4.2 (987 отзывов). Адрес: 2-201 Rinkūminamihama, Sennan, Osaka 590-0535, Япония	0101000020E6100000E9375D6060E86040BF02E2BF8A304140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
f788c69b-29ad-4bc9-a074-33b9bee52d49	Sayamaike Park	Establishment, park	Рейтинг Google: 4.3 (527 отзывов). Адрес: Ивамуро, Осакасаяма, Осака 589-0032, Япония	0101000020E610000041B0F4EB98F16040B6B3F9C962404140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
6101d253-2825-4c98-b927-f24e9a43e838	Expo '70 Commemorative Park	Establishment, museum	Рейтинг Google: 4.3 (21936 отзывов). Адрес: 10 Senribanpakukōen, Suita, Osaka 565-0826, Япония	0101000020E61000002B604C4409F1604099F4F75278674140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
99220a1d-2d8e-401f-8737-3a84232241d0	Ashihara Park	Establishment, park	Рейтинг Google: 3.4 (71 отзывов). Адрес: 2-chōme-1-1 Kuboyoshi, Naniwa Ward, Osaka, 556-0028, Япония	0101000020E610000003FE3A817AEF60403EE94482A9544140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
fd23ce9a-0e24-4109-b537-f7f46cd240e2	Ботанический сад Нагаи	Establishment, point of interest	Рейтинг Google: 4.3 (3338 отзывов). Адрес: 1-23 Nagaikōen, Higashisumiyoshi Ward, Osaka, 546-0034, Япония	0101000020E61000005BD3179DC7F06040FE6B2F58604E4140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
14590e53-7c7b-4dc9-b73f-1857ff5fd5fc	Saito Rainbow Park	Establishment, park	Рейтинг Google: 4.1 (1010 отзывов). Адрес: 2 Chome-3 Saitoaokita, Minoh, Osaka 562-0029, Япония	0101000020E61000000A9A3B9F66F060409647927B156E4140	f	f7ea1e32-ca79-41f2-9bcb-bb7dffebcbbf	\N
e4c8d8c7-17a3-4972-8166-d24e50925aa6	Sea World	Establishment, point of interest	Рейтинг Google: 4.5 (487 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, Nanyou, 太子路 邮政编码: 518060	0101000020E6100000E3FE23D3A17A5C40DD7BB8E4B87B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
081742e7-529a-4eff-a149-232017b17997	Shenzhen Bay Park	Establishment, point of interest	Рейтинг Google: 4.7 (165 отзывов). Адрес: GX43+J99, Nanshan, Shenzhen, Guangdong Province, Китай, 518065	0101000020E6100000F758FAD0057D5C40C636A968AC813640	f	812714b9-873b-41b9-b849-acb601551000	\N
ab42e063-f333-4d48-8304-9e2d843569b1	Shenzhen Central Park	Establishment, park	Рейтинг Google: 4.4 (3585 отзывов). Адрес: Futian District, Шэньчжэнь, Китай, 518039	0101000020E61000005323F433F5845C404B5AF10D858B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
e4e494b5-3838-4a41-ad04-ff095a6133f5	Lianhuashan Park	Establishment, park	Рейтинг Google: 4.4 (1094 отзывов). Адрес: 6030 Hong Li Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518036	0101000020E6100000A260C614AC835C405D4F745DF88D3640	f	812714b9-873b-41b9-b849-acb601551000	\N
d98903fe-3d9c-4d35-a6ad-d2b160711eb4	华侨城	Establishment, point of interest	Рейтинг Google: 4.2 (416 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, 华侨城片区 邮政编码: 518074	0101000020E6100000AED7F4A0A07E5C4024F25D4A5D8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
d8a47867-8381-4880-a01f-00ca64ef32b9	Shenzhen International Garden and Flower Expo Park	Establishment, park	Рейтинг Google: 4.2 (137 отзывов). Адрес: G2P2+5QH, Shen Nan Da Dao, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518041	0101000020E6100000132A38BC20805C402009FB7612893640	f	812714b9-873b-41b9-b849-acb601551000	\N
65d4ed81-3456-4814-9002-2ce7acbb137b	Maluan Mountain	Establishment, point of interest	Рейтинг Google: 4.8 (5 отзывов). Адрес: Китай, 广东省深圳市龙岗区M822+4PW 邮政编码: 518118	0101000020E61000003C003D6851935C4060AFB0E07EA63640	f	812714b9-873b-41b9-b849-acb601551000	\N
9a30c2b8-125c-45a8-8d02-4b0906f1e32c	Shenzhen Safari Park	Establishment, point of interest	Рейтинг Google: 4.1 (627 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, 西丽路465号 邮政编码: 518071	0101000020E61000008272DBBE477E5C40AE669DF17D993640	f	812714b9-873b-41b9-b849-acb601551000	\N
6bd83839-f62d-4997-b88d-b2265cb3002c	Splendid China Folk Culture Village (锦绣中华民俗村)	Establishment, point of interest	Рейтинг Google: 4.3 (43 отзывов). Адрес: 9003 Shen Nan Da Dao, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518058	0101000020E61000005CC246FE057F5C40CD3340B335883640	f	812714b9-873b-41b9-b849-acb601551000	\N
07383845-ccb6-4715-8a44-03b864ba780a	Lizhi Park	Establishment, park	Рейтинг Google: 4.2 (1198 отзывов). Адрес: 1001 Hong Ling Zhong Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518028	0101000020E61000009D66817687865C407520EBA9D58B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
6dc6f93a-358e-4f25-9b73-ef0acb32221c	Bijiashan Park	Establishment, park	Рейтинг Google: 4.3 (89 отзывов). Адрес: H37J+QQJ, Futian District, Shenzhen, Guangdong Province, Китай	0101000020E6100000C310397D3D855C403B71395E81903640	f	812714b9-873b-41b9-b849-acb601551000	\N
f5b0a3a0-6bd2-4721-bec0-55d6625f3830	仙湖植物园	Establishment, point of interest	Рейтинг Google: 4.3 (224 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 仙湖路160号 邮政编码: 518004	0101000020E610000006A79949AF8B5C401E328A8ADD933640	f	812714b9-873b-41b9-b849-acb601551000	\N
276b181d-bc58-4b39-b244-4aa4119df773	East Lake Park, Shenzhen	Establishment, park	Рейтинг Google: 4 (62 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 爱国路辅路H48V+PGC 邮政编码: 518018	0101000020E6100000BCE82B4833895C408196AE601B913640	f	812714b9-873b-41b9-b849-acb601551000	\N
5f4d673a-1c01-4782-bd5a-7cf9850c0171	Wutong Mountain	Establishment, park	Рейтинг Google: 4.4 (79 отзывов). Адрес: H6J4+J3V, Luohu District, Shenzhen, Guangdong Province, Китай, 518003	0101000020E610000013109370218D5C406DFE5F75E4943640	f	812714b9-873b-41b9-b849-acb601551000	\N
c9e49c72-f8e2-4a90-a3d0-250fb3599f90	Zhongshan Park	Establishment, park	Рейтинг Google: 4.3 (162 отзывов). Адрес: 3109 Nan Shan Da Dao, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518056	0101000020E6100000EEB5A0F7C67A5C409FC9FE791A8C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
f83fbaa0-d86e-4209-ad76-33b9c2abde05	The mixc mall	Establishment, point of interest	Рейтинг Google: 4.7 (66 отзывов). Адрес: GW8W+JF3, Nanshan, Shenzhen, Guangdong Province, Китай, 518064	0101000020E610000046F185248E7C5C4089601C5C3A843640	f	812714b9-873b-41b9-b849-acb601551000	\N
f008ec05-8aa4-4112-9f0a-45be906ba598	Lianhuashan Park （South Gate 1）	Establishment, park	Рейтинг Google: 4.4 (8 отзывов). Адрес: 6026 Hong Li Lu, 福田ＣＢＤ Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518038	0101000020E6100000E23AC61517845C40DA006C40848C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
64f242df-2417-46ad-b96c-3222ae59fc6b	Shenzhen Children's Park	Establishment, park	Рейтинг Google: 3.7 (59 отзывов). Адрес: 12 Tong Le Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518208	0101000020E610000089981249F4875C400B7BDAE1AF8D3640	f	812714b9-873b-41b9-b849-acb601551000	\N
29fc4e82-29a4-4809-a636-5ffcaf9466b3	Tequila Coyote's Mexican Restaurant	Establishment, food	Рейтинг Google: 4.9 (261 отзывов). Адрес: 20-21 Tai Zi Lu, 20, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518060	0101000020E6100000224F92AE997A5C4040F67AF7C77B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
1f746411-6e76-40ba-9a9a-5924e66bdce6	Gaga Chef	Establishment, food	Рейтинг Google: 5 (10 отзывов). Адрес: Китай, Shen Zhen Shi, Nan Shan Qu, CN 广东省 深圳市 南山区 深南大道 9668 9668号万象天地NL110 邮政编码: 518058	0101000020E61000004260E5D0227D5C40895E46B1DC8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
0d6d7592-ad77-41ab-a9d0-adcd6d4a1938	Ensue	Establishment, food	Рейтинг Google: 4.8 (18 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 福田ＣＢＤ福田香格里拉大酒店 邮政编码: 518046	0101000020E610000013A342D0AC835C401BE038DF3E893640	f	812714b9-873b-41b9-b849-acb601551000	\N
493d1fc3-fdf6-4f6a-be0f-ca5bce275337	Tiangong Restaurant	Establishment, food	Рейтинг Google: 5 (1 отзывов). Адрес: Китай, Shen Zhen Shi, Luo Hu Qu, 大剧院B出口 CN 广东省 深圳市 罗湖区 深南东路 5016 5016号京基100大厦A座 邮政编码: 518010	0101000020E6100000DB334B02D4865C406C21C841098B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
ff6f4433-c73a-46c2-9371-3ba6c6189b76	Muslim Restaurant	Establishment, food	Рейтинг Google: 4.8 (14 отзывов). Адрес: JRXG+6C7, Dong Fu Wei Dong Jie, Bao An Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518128	0101000020E6100000B8AE9811DE745C40785E2A36E6A53640	f	812714b9-873b-41b9-b849-acb601551000	\N
86bba304-5ef7-4fba-abc2-097dd49abfff	Man Ho Chinese Restaurant	Establishment, food	Рейтинг Google: 5 (5 отзывов). Адрес: Китай, Shen Zhen Shi, Fu Tian Qu, JW万豪酒店 CN 广东省 深圳市 福田区 深南大道 6005 6005号金茂 邮政编码: 518042	0101000020E61000004BEA043411825C40EFFE78AF5A893640	f	812714b9-873b-41b9-b849-acb601551000	\N
989bf4fc-130b-4b6a-9b64-747a9b3c2a44	Flavorz全日餐厅	Establishment, food	Рейтинг Google: 4 (10 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 中心城 Fu Hua San Lu, 116号深圳星河丽思卡尔顿酒店2层 邮政编码: 518046	0101000020E61000005B96AFCBF0835C40280CCA349A883640	f	812714b9-873b-41b9-b849-acb601551000	\N
f3b5fa9e-09f7-4193-88a2-bde09e0bcb93	Mandarin Oriental Shenzhen	Establishment, lodging	Рейтинг Google: 4.9 (62 отзывов). Адрес: Block A UpperHills No, 5001 Huang Gang Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518026	0101000020E610000022156B5D8F845C409525DF11BA8E3640	f	812714b9-873b-41b9-b849-acb601551000	\N
6b8b7944-2fc9-45b1-8975-634c57a6f4ca	Bus grill	Establishment, food	Рейтинг Google: 4.4 (115 отзывов). Адрес: Китай, Shen Zhen Shi, Fu Tian Qu, 福田ＣＢＤ Min Tian Lu, No.134, 135-D, North Yard Block 邮政编码: 518048	0101000020E6100000E281B7F674835C40D1F12C9CFF883640	f	812714b9-873b-41b9-b849-acb601551000	\N
3d8d4ce8-1d7e-4404-bdfc-09f5fcbabc8e	Mama mia Indian	Establishment, food	Рейтинг Google: 4.8 (5 отзывов). Адрес: FWMC+Q7C, Nanyou, Nanshan, Shenzhen, Guangdong Province, Китай, 518060	0101000020E61000007677F8C6EB7A5C40161CB9C9037C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
787bb652-8c57-4b35-8b18-5edfbbf47283	宝莱坞印度菜原味馆	Establishment, food	Рейтинг Google: 4.4 (59 отзывов). Адрес: Luohu District, Шэньчжэнь, Китай	0101000020E610000000E1438996875C4040A54A94BD893640	f	812714b9-873b-41b9-b849-acb601551000	\N
476463e0-ada6-41eb-9da5-ebe02267d57b	Xianggong	Establishment, food	Рейтинг Google: 4.1 (194 отзывов). Адрес: 1002 Jian She Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518001	0101000020E61000008BEE0F4A4E875C403EC3E5C292883640	f	812714b9-873b-41b9-b849-acb601551000	\N
10d1fd66-b171-45cf-8f84-31205ec96b85	Tanyu	Establishment, food	Рейтинг Google: 5 (1 отзывов). Адрес: A, 043 区B1 Long Hua Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518131	0101000020E6100000DDB5847CD0815C402E1C08C902A63640	f	812714b9-873b-41b9-b849-acb601551000	\N
a0a4ace3-10f3-4a34-9c60-8926d34effed	王品台塑牛排	Establishment, food	Рейтинг Google: 4.5 (4 отзывов). Адрес: Nanshan, Шэньчжэнь, Китай, 518058	0101000020E6100000D68EE21C757E5C4097AC8A7093893640	f	812714b9-873b-41b9-b849-acb601551000	\N
3118db1c-69e5-465e-9492-71b8647d84d9	Mo Bar - Mandarin Oriental, Shenzhen	Bar, establishment	Рейтинг Google: 4.6 (12 отзывов). Адрес: A座, 79楼, 深业上城, 5001 Huang Gang Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518026	0101000020E61000007B2FBE688F845C4083BAEDE7B98E3640	f	812714b9-873b-41b9-b849-acb601551000	\N
36ec2c69-a65a-4442-b86e-8de3d02f2a30	Shizuku	Establishment, food	Рейтинг Google: 5 (1 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, Shen Nan Da Dao, 6025号英龙大厦 邮政编码: 518040	0101000020E61000009198A0866F815C408D9C853DED883640	f	812714b9-873b-41b9-b849-acb601551000	\N
b6a6220b-7069-40f9-b06a-e36d81a391f5	Yunjingxuan	Establishment, food	Рейтинг Google: 3.7 (3 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, Jia Bin Lu, 2002号彭年酒店 邮政编码: 518011	0101000020E6100000D367075CD7875C40996D0267848A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
bc1c3bfd-c994-4c7e-853b-06e7bb080d78	Futian Shangri-La, Shenzhen	Establishment, lodging	Рейтинг Google: 4.3 (1133 отзывов). Адрес: 4088 Yi Tian Lu, 中心城 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518048	0101000020E6100000085A8121AB835C406FD39FFD48893640	f	812714b9-873b-41b9-b849-acb601551000	\N
9376e02c-e040-49ca-bfe9-f2ade6abcd1e	Park Hyatt Shenzhen	Establishment, lodging	Рейтинг Google: 4.6 (118 отзывов). Адрес: 5023 Yi Tian Lu, 中心城 Fu Tian Qu, Shen Zhen Shi, Китай, 518046	0101000020E61000003A60B24C9A835C403D16365E15893640	f	812714b9-873b-41b9-b849-acb601551000	\N
53eb1ff1-4213-456b-8a5f-51cb958fb5ab	The Langham, Shenzhen	Establishment, lodging	Рейтинг Google: 4.4 (349 отзывов). Адрес: 7888 Shen Nan Da Dao, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518040	0101000020E6100000833C71EF50815C409D9E776341893640	f	812714b9-873b-41b9-b849-acb601551000	\N
19ad408c-fbdf-4132-9c0c-6260b63a331f	Knight Valley	Establishment, point of interest	Рейтинг Google: 3.7 (33 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Yan Tian Qu, 879县道J79Q+G9Q 邮政编码: 518085	0101000020E6100000C3EFA65B76925C408D2958E36C9E3640	f	812714b9-873b-41b9-b849-acb601551000	\N
2526025a-12f6-48c3-aec4-6fcab845d5ad	Shenzhen Talent Park	Establishment, parking	Рейтинг Google: 4.7 (35 отзывов). Адрес: GW6W+FFQ, Nanshan, Shenzhen, Guangdong Province, Китай, 518065	0101000020E61000009F083DF68E7C5C404CB0EE0EDF823640	f	812714b9-873b-41b9-b849-acb601551000	\N
f042f833-34a0-4dca-b0d0-4985d574d5de	荷兰花卉小镇	Establishment, point of interest	Рейтинг Google: 4 (113 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, 南头月亮湾大道3008号 邮政编码: 518056	0101000020E61000001E61623D7F7A5C403F94C382568B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
b4de499e-bb85-42e5-8865-449a0cd83a26	Nanshan Kitchen, Shenzhen Marriott Hotel Nanshan	Establishment, point of interest	Рейтинг Google: 5 (1 отзывов). Адрес: Китай, GuangdongshengShenzhenshi Nan Shan Qu, Haide 88 Yi Road Level 6blk A, Scc Bldg Level 6, Block A, Scc Building 邮政编码: 518054	0101000020E6100000ECDD1FEF557B5C40595E036C51863640	f	812714b9-873b-41b9-b849-acb601551000	\N
3ec49022-7222-44a3-b0ad-0d58c184f3bd	Dongmen Pedestrian Street Legislative Jiaoyushi	Establishment, point of interest	Рейтинг Google: 4.5 (223 отзывов). Адрес: G4VC+M9V, Shen Nan Dong Lu, 东门 Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай	0101000020E610000099F04BFDBC875C407024D060538B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
ffd721a6-b3e3-4ada-8634-185d92b83421	龙津石塔	Establishment, point of interest	Рейтинг Google: 4 (6 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Bao An Qu, 桥东五巷 邮政编码: 518104	0101000020E61000008481E7DEC3735C4081EB8A19E1BD3640	f	812714b9-873b-41b9-b849-acb601551000	\N
b898286e-d607-4c95-9e59-669ac472967c	深圳市大鹏古城博物馆	Establishment, point of interest	Рейтинг Google: 3.2 (13 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Long Gang Qu, 大鹏街道鹏城社区HGV7+P8F 邮政编码: 518120	0101000020E61000004F4F690EDAA05C407C58B96125983640	f	812714b9-873b-41b9-b849-acb601551000	\N
14153f03-66d7-44b0-b365-b3f72976bd65	Futian Mangrove Nature Reserve	Establishment, point of interest	Рейтинг Google: 3.8 (4 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, Bin Hai Da Dao, 附近 邮政编码: 518041	0101000020E61000005C72DC291D805C405890662C9A863640	f	812714b9-873b-41b9-b849-acb601551000	\N
cffcc51f-79cb-446a-88c8-009d776089b1	Смотровая площадка	Establishment, point of interest	Рейтинг Google: 3.3 (71 отзывов). Адрес: Deep Bay Rd, Lau Fau Shan, Гонконг	0101000020E61000003F6DF9ED90805C40D8CF07701F7C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
c387aba5-a85e-4cfc-822b-4596f1f61ea0	深圳欢乐谷	Amusement park, establishment	Рейтинг Google: 4.3 (34 отзывов). Адрес: Китай, 广东省深圳市南山区华侨城GXRJ+M69 邮政编码: 518074	0101000020E610000043DDAC66C27E5C40FC219111AB8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
c6b8b786-d1d9-4a83-b696-8cd3cb32e731	Shenzhen Mosque	Establishment, mosque	Рейтинг Google: 4.9 (153 отзывов). Адрес: 7 Mei Lin Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518049	0101000020E6100000DB4E5B2382845C4061C3D32B65913640	f	812714b9-873b-41b9-b849-acb601551000	\N
ae21d178-5d3e-49e1-b0a5-394c6114050e	深圳圣安多尼堂	Church, establishment	Рейтинг Google: 4.8 (37 отзывов). Адрес: G2V7+MVM, Futian District, Shenzhen, Guangdong Province, Китай, 518043	0101000020E61000006744696FF0805C40D751D504518B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
e1a50791-5448-47a0-900e-ae109f4b0119	Hongfa Temple	Establishment, place of worship	Рейтинг Google: 4.6 (66 отзывов). Адрес: H5HJ+4JJ, Luohu District, Shenzhen, Guangdong Province, Китай, 518003	0101000020E6100000BBD39D279E8B5C401B0FB6D8ED933640	f	812714b9-873b-41b9-b849-acb601551000	\N
120373c8-1243-432e-8791-d808e44835ad	Shenzhen Bay Park Liuhuashan	Establishment, park	Рейтинг Google: 4.4 (27 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, Sha He Xi Lu, 滨海大道	0101000020E610000091628044137D5C4012FA997ADD823640	f	812714b9-873b-41b9-b849-acb601551000	\N
ff61fb13-00fe-4d6b-b336-71f6092d0e48	People's Park	Establishment, park	Рейтинг Google: 4 (334 отзывов). Адрес: 3071 Ren Min Bei Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518001	0101000020E6100000CFA0A17F82875C4057EBC4E5788D3640	f	812714b9-873b-41b9-b849-acb601551000	\N
fa7e63c8-175f-498f-8d74-fd12dda31238	Shenzhen Central Park （West Gate）	Establishment, park	Рейтинг Google: 4.1 (44 отзывов). Адрес: G3JG+F37, Huang Gang Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518039	0101000020E61000008A75AA7CCF845C401B2C9CA4F9873640	f	812714b9-873b-41b9-b849-acb601551000	\N
b240974c-611f-422c-a145-840535a748d2	World Sculpture Park	Establishment, point of interest	Рейтинг Google: 4.7 (29 отзывов). Адрес: Китай, 广东省深圳市南山区华侨城GXPC+2HV 邮政编码: 518058	0101000020E6100000A2ED98BA2B7E5C405B99F04BFD883640	f	812714b9-873b-41b9-b849-acb601551000	\N
83635c8f-4586-4949-8da2-d728e273fbbe	Xiangmi Park	Establishment, park	Рейтинг Google: 4.3 (45 отзывов). Адрес: 30 Nong Yuan Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518040	0101000020E6100000F4C473B680815C40AFCF9CF5298B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
0ea60b58-63c4-426f-8bb8-022d493ce441	Sihai Park （North Gate）	Establishment, park	Рейтинг Google: 4.1 (59 отзывов). Адрес: 6 Gong Yuan Lu, Nanyou, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518060	0101000020E6100000E728F686317B5C40C3842C66DF7E3640	f	812714b9-873b-41b9-b849-acb601551000	\N
3364f029-0cb4-4e2a-adf1-b30c4d23f15f	Парк водно-болотных угодий Гонконга	Establishment, park	Рейтинг Google: 4.2 (5632 отзывов). Адрес: Wetland Park Rd, Tin Shui Wai, Гонконг	0101000020E610000034CD85DB6B805C40F2B4FCC055783640	f	812714b9-873b-41b9-b849-acb601551000	\N
d0e0dea8-8318-4a48-9fc7-6438225e005d	Qianhai Flower Park	Establishment, park	Рейтинг Google: 4 (43 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, 南头月亮湾大道GWW6+499 邮政编码: 518056	0101000020E610000079CBD58F4D7A5C40A08A1BB7988B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
9f0c2c57-0102-47e0-a73d-ff8cccc32522	Парк Хейджинг Роуд Дейзуанг	Establishment, park	Рейтинг Google: 5 (2 отзывов). Адрес: G6WQ+F2F 湾, Shatoujiao Neighborhood, Yantian District, 海边 Guangdong Province, Китай	0101000020E61000007ADFF8DA338F5C40401361C3D38B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
8e98c6b6-3570-401a-850c-916c2f0ee09c	Futian Mangrove Forest Park N. Gate	Establishment, park	Рейтинг Google: 4.3 (3 отзывов). Адрес: Китай, Shen Zhen Shi, Fu Tian Qu, 红树林生态公园 CN 广东省 深圳市 福田区 新洲路与福荣路交叉口旁 邮政编码: 518042	0101000020E61000007094BC3AC7825C405E68AED348833640	f	812714b9-873b-41b9-b849-acb601551000	\N
f500b75d-380d-498b-ae80-5481cba26d54	Пешеходный маршрут	Establishment, point of interest	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Архыз, Карачаево-Черкесская Республика, Россия, 369152	0101000020E610000099E436D0329744403E59D6A2AAC64540	f	812714b9-873b-41b9-b849-acb601551000	\N
e9ac8545-9ebb-4192-b79a-26b47681e671	Lianhuashan Park Fengzheng Square	Establishment, point of interest	Рейтинг Google: 4.8 (12 отзывов). Адрес: G3X5+QX7, Hong Li Lu, 福田ＣＢＤ Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518000	0101000020E610000004ADC090D5835C40F2B391EBA68C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
95aae63e-6075-4153-afad-8d56e4c1a190	Oct Harbour	Establishment, lodging	Рейтинг Google: 4.2 (6 отзывов). Адрес: No.2008 Binhai Avenue, The, 沙河西路南山区深圳市广东省 Китай, 518053	0101000020E6100000545227A0897F5C404628B682A6853640	f	812714b9-873b-41b9-b849-acb601551000	\N
3844d531-b776-41de-8c50-84e599b0ddb8	Intercontinental Shenzhen Dameisha Resort	Establishment, lodging	Рейтинг Google: 4.5 (55 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Yan Tian Qu, 盐葵路9号 邮政编码: 518083	0101000020E61000005D6DC5FEB2935C4024ED461FF3993640	f	812714b9-873b-41b9-b849-acb601551000	\N
805eda96-c336-4d38-a410-6fada468db2e	Hilton Shenzhen Shekou Nanhai	Establishment, lodging	Рейтинг Google: 4.6 (254 отзывов). Адрес: 1177 Wang Hai Lu, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518067	0101000020E61000007C725EADA47A5C402B508BC1C37A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
e03260ec-dd42-40f1-80a5-da607d31de28	Xiaomeisha Sea World Resort Parking Lot	Establishment, parking	Рейтинг Google: 4.2 (6 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Yan Tian Qu, 盐坝高速出口J82G+XR5 邮政编码: 518083	0101000020E610000056F31C91EF945C40D8ADAFBF369A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
11927b24-11e0-4266-bd13-f04e27142beb	Hard Rock Hotel Shenzhen	Establishment, lodging	Рейтинг Google: 4.5 (501 отзывов). Адрес: No. 9 Mission Hills Road, 龙华区深圳市广东省 Китай, 518110	0101000020E610000083177D0569845C40B492567C43B93640	f	812714b9-873b-41b9-b849-acb601551000	\N
97b87bd1-5cb5-41fd-811d-008c435f5465	Grand Mercure Shenzhen Guangming	Establishment, lodging	Рейтинг Google: 4.3 (20 отзывов). Адрес: Building, Yuefu Square, 光明区深圳市广东省 Китай, 518107	0101000020E61000000AD9791B9B7B5C404B033FAA61BF3640	f	812714b9-873b-41b9-b849-acb601551000	\N
aead7bdf-c3f6-4adc-9d28-a6217849f5b4	OCT East	Establishment, point of interest	Рейтинг Google: 3 (2 отзывов). Адрес: Китай, 广东省深圳市盐田区中心城G3V5+64Q 邮政编码: 518000	0101000020E610000051A5660FB4835C40A296E656088B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
434fbd36-4e4b-424e-be17-6ff3d0000a1d	Dameisha Seashore Park	Establishment, park	Рейтинг Google: 4.5 (40 отзывов). Адрес: 99 Yan Mei Lu, Yan Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518085	0101000020E6100000EBE2361AC0935C40390B7BDAE1973640	f	812714b9-873b-41b9-b849-acb601551000	\N
8a8abf1e-566f-4293-b761-d9ec1517ecaa	Shenzhen Lavenna Resort	Establishment, lodging	Рейтинг Google: 4.6 (5 отзывов). Адрес: Китай, Shen Zhen Shi, Ping Shan Qu, 大鹏新区新东路28号 邮政编码: 518121	0101000020E6100000D90A9A9658985C401B800D8810BF3640	f	812714b9-873b-41b9-b849-acb601551000	\N
23b007c7-73d7-4bcd-bba4-655f1b16088d	桔钓沙	Establishment, point of interest	Рейтинг Google: 5 (3 отзывов). Адрес: Китай, Shen Zhen Shi, Long Gang Qu, 南澳街道东山社区街道海滩 邮政编码: 518120	0101000020E610000031E24C5DC39E5C4032ACE28DCC953640	f	812714b9-873b-41b9-b849-acb601551000	\N
494ab3a3-8166-4e3e-ae3d-5330d36e5b8d	You Gan Bay Resort-Nanao Town, Shenzhen City.	Establishment, lodging	Рейтинг Google: 3.1 (7 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Long Gang Qu, 柚柑湾度假村FFJR+39C 邮政编码: 518121	0101000020E61000007C0C569C6A9F5C4086AB0320EE7A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
c4568ae1-c76d-4422-8ad7-d274b7df02f3	Sheraton Dameisha Resort, Shenzhen	Establishment, lodging	Рейтинг Google: 4.2 (50 отзывов). Адрес: 9 Yankui Road, 盐田区深圳市广东省 Китай, 518083	0101000020E61000005D6DC5FEB2935C4024ED461FF3993640	f	812714b9-873b-41b9-b849-acb601551000	\N
a6f04443-60ab-4a47-ab6e-b2973bda17fa	Xichong Public Beach Toll Gate 1	Establishment, point of interest	Рейтинг Google: 4.3 (6 отзывов). Адрес: FGGJ+625, Nan Xi Lu, Long Gang Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518121	0101000020E61000009373620FEDA15C404D874ECFBB793640	f	812714b9-873b-41b9-b849-acb601551000	\N
5d6f5984-b194-4eb9-bdc7-47c9f9eb4a93	Lavenna Resort Judiaosha	Establishment, lodging	Рейтинг Google: 3 (4 отзывов). Адрес: No.28 Xindong Road, 龙岗区深圳市广东省 Китай, 518131	0101000020E61000009A081B9E5EA35C403C31EBC5508E3640	f	812714b9-873b-41b9-b849-acb601551000	\N
a07c674d-9bdd-430a-b651-a0ec2edc0342	Shenzhen Dapeng Fortress Entrance Parking	Establishment, parking	Рейтинг Google: 5 (5 отзывов). Адрес: HGV7+4QR, Longgang, Shenzhen, Guangdong Province, Китай, 518120	0101000020E610000093A7ACA6EBA05C402FBFD364C6973640	f	812714b9-873b-41b9-b849-acb601551000	\N
bb22e0b1-5958-4cf2-954f-d66bacdff5bc	Holdfound. Dongchong Beachfront Hotel	Establishment, lodging	Рейтинг Google: 4 (6 отзывов). Адрес: FHQM+692, Longgang, Shenzhen, Guangdong Province, Китай, 518121	0101000020E6100000577A6D3656A55C401BF5108DEE7C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
2693ca20-d0ed-4fdc-8d54-fd4c9e9a58f5	Fairfield By Marriott Shenzhen Bao'An	Establishment, lodging	Рейтинг Google: 4.5 (11 отзывов). Адрес: PR79+5R6, Xinqiao, Sub-District, Shenzhen, Guangdong Province, Китай, 518104	0101000020E61000007EAB75E272745C40C440D7BE80B63640	f	812714b9-873b-41b9-b849-acb601551000	\N
94123626-f7f7-4cee-9d85-019f84881933	Fairfield BY Marriott Shenzhen Dameisha	Establishment, lodging	Рейтинг Google: 3.3 (7 отзывов). Адрес: NO, 1 SONGCAI ROAD, 盐田区深圳市 Shenzhen, Китай, 518000	0101000020E61000004815C5ABAC935C40CCB6D3D688983640	f	812714b9-873b-41b9-b849-acb601551000	\N
4e1066e7-34c9-41c2-885c-a036ef48ba8d	Grand Skylight	Establishment, lodging	Рейтинг Google: 4.4 (89 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 深南中路3024号 邮政编码: 518039	0101000020E610000045D8F0F44A855C406DFFCA4A938A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
50434231-1cfc-4b62-9ffb-96305c4a34d9	Shenzhen Art Museum	Establishment, museum	Рейтинг Google: 3.9 (25 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 爱国路东湖公园内 邮政编码: 518021	0101000020E6100000FA6184F068895C40B60E0EF626923640	f	812714b9-873b-41b9-b849-acb601551000	\N
a9b972da-2c4a-4b11-a8c6-a0cb1e282f4e	深圳博物館	Establishment, museum	Рейтинг Google: 4.5 (8 отзывов). Адрес: 市民中心A区, G3V5+MH8, Fu Zhong Lu, 中心城 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518000	0101000020E610000071C806D2C5835C40A835CD3B4E8B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
ae5b9c8f-3b08-4623-bbeb-d83028b07f1e	He Xiangning Art Museum	Establishment, museum	Рейтинг Google: 4.4 (248 отзывов). Адрес: 9013 Shen Nan Da Dao, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518053	0101000020E610000094A12AA6D27E5C405AF2785A7E883640	f	812714b9-873b-41b9-b849-acb601551000	\N
1ae8f56e-27b7-4842-8c07-6530fe74a9aa	Yachang Art Gallery	Establishment, museum	Рейтинг Google: 4.3 (6 отзывов). Адрес: H3C8+MWP, Cai Tian Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518049	0101000020E61000008A027D224F845C40EFE4D3635B923640	f	812714b9-873b-41b9-b849-acb601551000	\N
565caef7-5371-4c76-92d6-ebb2306a8f54	Museum of Contemporary Art & Planning Exhibition	Establishment, museum	Рейтинг Google: 4.6 (44 отзывов). Адрес: 184 Fu Zhong Lu, 中心城 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518000	0101000020E6100000F83E0BF8EB835C4029CFBC1C768B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
0c5256ab-5380-40e4-a263-5d81ef5f1f6d	Gushengwu Museum	Establishment, point of interest	Рейтинг Google: 3.6 (5 отзывов). Адрес: H5MG+QVW, Luohu District, Shenzhen, Guangdong Province, Китай, 518003	0101000020E610000003ECA353578B5C404EB51666A1953640	f	812714b9-873b-41b9-b849-acb601551000	\N
51466ac7-9eba-4e4c-b67c-c07facba4d40	海上世界文化藝術中心	Establishment, museum	Рейтинг Google: 4.1 (34 отзывов). Адрес: 1187 Wang Hai Lu, 蛇口 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай	0101000020E61000009C89E942AC7A5C4024F0879FFF7A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
8d8bef79-5e86-4785-9644-3cd3d7a7e100	Nantou Ancient City Museum	Establishment, museum	Рейтинг Google: 4.3 (87 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, Shen Nan Da Dao, 南头较场2号 邮政编码: 518056	0101000020E6100000A4C16D6DE17A5C400BD0B69A758A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
ab15bb5f-c15f-494c-a28c-31d81fe8aa11	Shenzhen Contemporary Art Museum	Art gallery, establishment	Рейтинг Google: 4.3 (7 отзывов). Адрес: Китай, 附近 Fu Tian Qu, 中心城 Shi Min Zhong Xin CN 广东省 深圳市 邮政编码: 518000	0101000020E6100000C780ECF5EE835C4096ECD808C48B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
30a0a9c1-932d-4423-a1d9-d2c3c33465c2	Tianhou Museum	Establishment, museum	Рейтинг Google: 4.6 (28 отзывов). Адрес: 9 Chi Wan Liu Lu, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518068	0101000020E6100000A438471D1D795C4045B75ED3837A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
ed287530-ae41-48ec-a4fc-36846ec06346	Hua Art Museum	Establishment, museum	Рейтинг Google: 3.8 (18 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, Shen Nan Da Dao, 9009号-1 邮政编码: 518053	0101000020E6100000E2AC889AE87E5C400647C9AB73883640	f	812714b9-873b-41b9-b849-acb601551000	\N
9e1b3a03-28dc-4b53-b34c-3cf2c95e205b	Huaxia Art Centre	Establishment, museum	Рейтинг Google: 4.2 (5 отзывов). Адрес: 1 Guang Qiao Jie, 华侨城 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518053	0101000020E6100000637AC2120F7F5C4058552FBFD3883640	f	812714b9-873b-41b9-b849-acb601551000	\N
174c40b8-a87c-46d5-aa1c-ffe0ea099e92	當代藝術與都市計畫展覽館	Establishment, museum	Рейтинг Google: 4.4 (10 отзывов). Адрес: G3W6+7QP, Fu Zhong Lu, 中心城 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518000	0101000020E6100000999B6F44F7835C4080B33973B48B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
6db78418-4271-4763-afc7-1c1932c8a6a5	Shenzhen Concert Hall	Establishment, parking	Рейтинг Google: 4.4 (85 отзывов). Адрес: 2016 Fu Zhong Yi Lu, 福田ＣＢＤ Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518048	0101000020E61000003221E692AA835C4098A432C51C8C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
5d9a56f4-6933-430c-a268-499dc5eba22a	Shenzhen Grand Theatre	Establishment, point of interest	Рейтинг Google: 4.1 (413 отзывов). Адрес: 5018 Shen Nan Dong Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518010	0101000020E610000050C24CDBBF865C4003CDE7DCED8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
2eb58272-98ef-4efe-8520-0b9a7da76042	Shenzhen World Exhibition & Convention Center	Establishment, point of interest	Рейтинг Google: 4.6 (297 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Bao An Qu, 福海街道展城路1号 邮政编码: 518103	0101000020E61000001442075D42715C4091E1C2CB1DB33640	f	812714b9-873b-41b9-b849-acb601551000	\N
a3ca86d3-e50c-474b-b392-b8a9d875b5a4	Shenzhen Convention & Exhibition Center	Establishment, point of interest	Рейтинг Google: 4.2 (418 отзывов). Адрес: G3J5+7XW, Fu Hua San Lu, 中心城 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518017	0101000020E61000003317B83CD6835C40D0F0660DDE873640	f	812714b9-873b-41b9-b849-acb601551000	\N
3c11a5bd-c5f6-4d15-b62f-892efca91574	Shenzhen Cultural Center	Establishment, museum	Рейтинг Google: 4.7 (23 отзывов). Адрес: 2 Jing Tian Dong Yi Jie, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518034	0101000020E6100000C3A04CA3C9825C4012C2A38D238E3640	f	812714b9-873b-41b9-b849-acb601551000	\N
a10cd0dc-e4d2-4852-a709-ee0b02570764	The Mixc of Shenzhen City Crossing	Establishment, point of interest	Рейтинг Google: 4.2 (529 отзывов). Адрес: 1881 Bao An Nan Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай	0101000020E6100000B83F170D19875C406F7F2E1A328A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
0b4e3b95-4440-4e95-966a-9d8146583295	Sungang Stationery Toy Gift Wholesale Market	Establishment, point of interest	Рейтинг Google: 4 (66 отзывов). Адрес: 1025 Bao An Bei Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518023	0101000020E6100000884A2366F6865C407BDAE1AFC98E3640	f	812714b9-873b-41b9-b849-acb601551000	\N
ca26aca2-61f4-4e23-9d85-52bcf0d59a71	Yitian Holiday Plaza	Establishment, point of interest	Рейтинг Google: 4.2 (95 отзывов). Адрес: 9028 Shen Nan Da Dao, 东门 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518058	0101000020E610000006103E94687E5C405FCFD72C97893640	f	812714b9-873b-41b9-b849-acb601551000	\N
f0c44db2-63ac-4c17-ac2b-eac4ae457439	Shenzhen Civic Center District Administrative Service Hall B	Establishment, point of interest	Рейтинг Google: 4.8 (22 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 中心城市民中心一层 邮政编码: 518000	0101000020E6100000C286A757CA835C406022DE3AFF8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
22b85263-b2e0-49a9-83e8-1c843343cb58	Shenzhen Library	Establishment, library	Рейтинг Google: 4.4 (127 отзывов). Адрес: 2001 Fu Zhong Yi Lu, 中心城 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518000	0101000020E61000007A1B9B1DA9835C40A723809BC58B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
35ad1bbc-fbf0-41d4-b6cb-ce0a2b8d0ab5	Dafen Art Museum	Establishment, museum	Рейтинг Google: 3.6 (46 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Long Gang Qu, 老围东三巷J45Q+Q5M 邮政编码: 518112	0101000020E6100000C9C859D8D3885C40E5D3635B069C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
b530a022-3597-48cd-84e2-51b95f10ab58	Shenzhen Culture Creative Park （West Gate）	Establishment, point of interest	Рейтинг Google: 3.3 (9 отзывов). Адрес: G28V+RW8, Yi Hao Lu, 新洲 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518042	0101000020E6100000F3C64961DE825C40842EE1D05B843640	f	812714b9-873b-41b9-b849-acb601551000	\N
4f583792-5a40-4ce6-a4dc-a175dae8e542	Graffiti Alley	Establishment, point of interest	Рейтинг Google: 5 (5 отзывов). Адрес: Tai Ping Shan St, Tai Ping Shan, Гонконг	0101000020E6100000DC0CDC2681895C403CD3F0D2F2483640	f	812714b9-873b-41b9-b849-acb601551000	\N
864e1f01-9503-4064-87a2-dd5af45351df	Kam Tin Mural Village	Establishment, museum	Рейтинг Google: 3.8 (480 отзывов). Адрес: 錦田市 中心, Yuen Long District, Гонконг	0101000020E6100000AC1919E42E845C408D19F2199A703640	f	812714b9-873b-41b9-b849-acb601551000	\N
edce4dab-0659-4125-9feb-1bab5b7ad46c	Jingzhifang	Establishment, food	Рейтинг Google: 4.8 (30 отзывов). Адрес: Китай, Shen Zhen Shi, Nan Shan Qu, 14, Wen Chang Nan Jie, 14号CN 广东省 深圳市 南山区 香山东街 邮政编码: 518074	0101000020E610000072DC291DAC7F5C4099D87C5C1B8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
4df76515-3bae-4757-a5c8-8c46351354f2	Paletto意大利餐厅	Establishment, food	Рейтинг Google: 4.4 (13 отзывов). Адрес: 中心城 Futian District, Шэньчжэнь, Китай, 518046	0101000020E6100000A35C1ABFF0835C402FF7C95180883640	f	812714b9-873b-41b9-b849-acb601551000	\N
f446ddeb-d277-499d-b104-5f7faa3bda99	Magpie Restaurant 喜鹊派餐厅	Establishment, food	Рейтинг Google: 4.6 (23 отзывов). Адрес: GXQV+V48, Wen Chang Nan Jie, 华侨城 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518074	0101000020E61000005A3D714A8A7F5C40AA605452278A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
7a446d3a-b939-4c92-b6a6-b19774111aa2	Bollywood Cafe (Hai An Cheng)	Establishment, food	Рейтинг Google: 4.1 (44 отзывов). Адрес: Shop44-45,2/F Area A, Poly Cultural Centre, 文心六路南油南山区深圳市广东省 Китай, 518054	0101000020E61000000B410E4A187C5C404F0DEA1159843640	f	812714b9-873b-41b9-b849-acb601551000	\N
274d588c-3c69-4156-87d3-640685389db3	Four Seasons - Shenzhen - Matsu Yi	Establishment, point of interest	Рейтинг Google: 3.7 (3 отзывов). Адрес: Китай, GuangdongShenzhen Fu Tian Qu, 中心城Futian District138-6/F FUTIAN DISTRICT FUHUA 邮政编码: 518048	0101000020E610000009FA0B3D62835C40598B4F01308A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
09c2afc0-1672-4f62-a67f-8fa694c72321	HH Gourmet	Establishment, food	Рейтинг Google: 4 (7 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, Wang Hai Lu, 1089-29号南海玫瑰园二期43-B商铺 邮政编码: 518060	0101000020E61000006CE80BC62D7B5C408BE88D49357C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
2b06d01e-3960-4f69-81ca-839991ee102f	Starbucks	Cafe, establishment	Рейтинг Google: 4.4 (25 отзывов). Адрес: Китай, Shen Zhen Shi, Nan Shan Qu, CN 广东省 深圳市 南山区 台北101 华侨城东部工业区E5 邮政编码: 518053	0101000020E610000031E47DC1937F5C40D73D682C50893640	f	812714b9-873b-41b9-b849-acb601551000	\N
768e734e-e260-4e6d-9484-95ea3693417f	星巴克咖啡starbucks coffee地王大厦店	Cafe, establishment	Рейтинг Google: 3.6 (16 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 深南东路5002号 邮政编码: 518010	0101000020E6100000FEB4519D0E875C40D3DA34B6D78A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
e53674e6-3cf2-4e4b-9cf2-d02d5b2fedc2	KK Mall	Establishment, point of interest	Рейтинг Google: 4.1 (265 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, Shen Nan Dong Lu, 5016号京基100大厦A座 邮政编码: 518010	0101000020E61000002FC214E5D2865C400E12A27C418B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
f239eb6c-8f2b-498d-8dae-3772812d0599	Yantian Seafood Food Street	Establishment, food	Рейтинг Google: 3.7 (6 отзывов). Адрес: Китай, Shen Zhen Shi, Yan Tian Qu, CN 广东省 深圳市 盐田区 海鲜街 48 48号附近 邮政编码: 518085	0101000020E6100000598638D6C5915C40685C381092953640	f	812714b9-873b-41b9-b849-acb601551000	\N
92599c81-c728-4526-b2a5-eaf7a3759f3a	Seafood Street	Establishment, point of interest	Рейтинг Google: 4.3 (6 отзывов). Адрес: J826+726, Jin Sha Jie, Yan Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518085	0101000020E6100000DF71E547D7935C408A3E1F65C4993640	f	812714b9-873b-41b9-b849-acb601551000	\N
7a7c3aa4-8a1e-48a5-822c-eb936dda7256	Fanlou	Establishment, food	Рейтинг Google: 4.5 (128 отзывов). Адрес: 118-7 Zhen Hua Lu, 118, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518037	0101000020E61000004F3BFC3559855C40A56B26DF6C8B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
c39b5a1c-54fc-4a35-8754-c407257d2708	McDonald's	Establishment, food	Рейтинг Google: 3.8 (6 отзывов). Адрес: Yantian District, Шэньчжэнь, Китай, 518085	0101000020E61000005DA45016BE935C40FB75A73B4F983640	f	812714b9-873b-41b9-b849-acb601551000	\N
4d3ca08e-9646-4b31-8095-d83aaaf34f6d	光明招待所	Establishment, food	Рейтинг Google: 4.2 (22 отзывов). Адрес: Guangming, Шэньчжэнь, Китай, 518107	0101000020E6100000698A00A7777C5C40FB5A971AA1C33640	f	812714b9-873b-41b9-b849-acb601551000	\N
e6fb2ad3-7046-4112-93c8-f05ff15c490c	深圳福田香格里拉大酒店大堂酒廊	Bar, establishment	Рейтинг Google: 4.3 (6 отзывов). Адрес: 4088 Yi Tian Lu, 福田ＣＢＤ Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518048	0101000020E6100000C636A968AC835C40C19140834D893640	f	812714b9-873b-41b9-b849-acb601551000	\N
f8bd1f0d-996e-4811-b85e-1ed680ae325d	粤式风味	Establishment, food	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Bao An Qu, 帝堂路沙四高新园1号-054 邮政编码: 518104	0101000020E6100000909E228788725C40F7B0170AD8BE3640	f	812714b9-873b-41b9-b849-acb601551000	\N
c4ecbfff-3062-483e-be1d-86d578446134	Dawat Indian Restaurant	Establishment, food	Рейтинг Google: 4 (206 отзывов). Адрес: 101 Zhen Zhong Lu, 紫荆城商业广场 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518027	0101000020E610000069723106D6855C401C295B24ED8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
f4d894df-e2bd-41a5-9f78-7b1f89a5eee2	Grand Hyatt Hotel Shenzhen Western Restaurant	Establishment, food	Рейтинг Google: 4.2 (14 отзывов). Адрес: 1881 Bao An Nan Lu, 蔡屋围 Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай	0101000020E61000005F48E24023875C4082548A1D8D893640	f	812714b9-873b-41b9-b849-acb601551000	\N
f7b7c184-f518-4669-b0e8-24e6b31d5b5e	Cafe Chinois	Cafe, establishment	Рейтинг Google: 4.3 (4 отзывов). Адрес: Jin Mao Shen Zhen JW Wan Hao Jiu Dian, 6005 Shen Nan Da Dao, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518042	0101000020E61000003FCCB96F10825C403B87D79A52893640	f	812714b9-873b-41b9-b849-acb601551000	\N
ce2d9984-273c-4ae7-af34-9871f39b08be	The St Regis Shenzhen	Establishment, lodging	Рейтинг Google: 4.5 (334 отзывов). Адрес: 5016 Shen Nan Dong Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518001	0101000020E6100000A6098096D3865C40EBBEAD05078B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
e84f8788-2757-4dd0-b222-1810ec63385a	Auvers	Establishment, food	Рейтинг Google: 4.1 (16 отзывов). Адрес: Китай, Shen Zhen Shi, Fu Tian Qu, 中心城CN 广东省 深圳市 福田区 140 米 邮政编码: 518038	0101000020E6100000C32ADEC83C845C4029965B5A0D893640	f	812714b9-873b-41b9-b849-acb601551000	\N
4014e9dc-8980-4039-9e95-7ccf119b70a4	7:59 Завтраки и кофе	Establishment, food	Рейтинг Google: 4.4 (21 отзывов). Адрес: Депутатская ул., 63, ул. Сурикова, 10, Иркутск, Иркутская обл., Россия, 664000	0101000020E61000000373993F4B115A408B620333F0244A40	f	812714b9-873b-41b9-b849-acb601551000	\N
a676f97c-9dea-4ce3-a036-ccc09344e5dc	Gaga Garden	Establishment, food	Рейтинг Google: 3 (1 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, Nanyou, Li Yuan Lu, 201号, 9 9号 邮政编码: 518060	0101000020E6100000E65C8AABCA7A5C40F5B9DA8AFD7D3640	f	812714b9-873b-41b9-b849-acb601551000	\N
3ed4c7ee-3a36-4924-b1fb-059b9e57af35	Sentosa Hotel Shenzhen Feicui Branch	Establishment, lodging	Рейтинг Google: 4 (130 отзывов). Адрес: Nanshan, Шэньчжэнь, Китай, 518056	0101000020E610000057790261A77A5C400684D6C397893640	f	812714b9-873b-41b9-b849-acb601551000	\N
173fc028-aa49-4a20-957c-7d7da7692ad9	KFC	Establishment, food	Рейтинг Google: 3.5 (4 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, Xili, 西丽街道沙河西路与留仙大道交汇处 邮政编码: 518071	0101000020E610000010406A13277D5C4061E28FA2CE943640	f	812714b9-873b-41b9-b849-acb601551000	\N
74c5138e-b50d-45d7-b0c4-bd6d3027861e	Jinjiang Inn Shenzhen Airport Branch	Establishment, lodging	Рейтинг Google: 5 (4 отзывов). Адрес: 六巷, 23 Fu Wei Lu, Bao An Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518128	0101000020E610000002D4D4B2B5745C40A0C37C7901A63640	f	812714b9-873b-41b9-b849-acb601551000	\N
2a922e70-bd6b-4015-8273-77fa17459283	Vienna International Qianhai Branch	Establishment, lodging	Рейтинг Google: 4.5 (19 отзывов). Адрес: No.8 Xixiang St. Industrial Rd., 宝安区深圳市 Китай, 518102	0101000020E6100000454772F90F775C40C8D0B1834A903640	f	812714b9-873b-41b9-b849-acb601551000	\N
2e1e501a-8bf0-48e3-b001-a594fb0f1590	Pinchaju Vegetarian Restaurant	Establishment, food	Рейтинг Google: 4.2 (9 отзывов). Адрес: 1022 Ai Guo Lu, 黄贝岭 Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518003	0101000020E61000008F5B824273885C406A46ABFF188D3640	f	812714b9-873b-41b9-b849-acb601551000	\N
16cccd61-0216-49b8-bc4b-e8d8e78f6a49	Ruolanci Vegetarian	Establishment, food	Рейтинг Google: 4.7 (11 отзывов). Адрес: Китай, Shen Zhen Shi, Nan Shan Qu, 东8号8号欢乐海岸 CN 广东省 深圳市 南山区 白石路 邮政编码: 518053	0101000020E6100000BA313D61897F5C40035B25581C863640	f	812714b9-873b-41b9-b849-acb601551000	\N
bcfecf1f-919e-415b-81b0-e48bcea2543c	Qingtai Planet Modern Vegetarian	Establishment, food	Рейтинг Google: 4 (1 отзывов). Адрес: Китай, Shen Zhen Shi, Nan Shan Qu, Nanyou, CN 广东省 深圳市 南山区 文心五路 33 33号海岸城1层141-1 邮政编码: 518064	0101000020E6100000C05B2041F17B5C404D840D4FAF843640	f	812714b9-873b-41b9-b849-acb601551000	\N
c090bcab-824f-4e98-a9f5-699fd3f78410	Tian Zi Shu Shi	Establishment, food	Рейтинг Google: 5 (4 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 6026, Hong Li Lu, 6026号1楼关山月美术馆 邮政编码: 518038	0101000020E6100000357BA01518845C40DBA2CC06998C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
37d12e7b-ffe8-4247-aa49-098eb5c54b10	Masala Bites - Ma Ma Mia	Establishment, food	Рейтинг Google: 3.9 (30 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, Nanyou, shop 110, district-1, nanhai rose gardens 邮政编码: 518060	0101000020E6100000F67F0EF3E57A5C4096389787F17B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
74745cbe-cf0e-4c2b-a885-01d39755fc84	Yueyi Life Health Sushiyuan	Establishment, food	Рейтинг Google: 4.3 (12 отзывов). Адрес: 2107 Bao An Nan Lu, 蔡屋围 Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518022	0101000020E61000008F4D976A0B875C40CADC216A478C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
7d274cc0-ba66-4e1b-91bc-354bd581af88	Voisin Organique 邻舍有机餐厅	Establishment, food	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, Qiao Bei Yi Jie, 富田创意文化园117号 邮政编码: 518072	0101000020E610000024F48EAE2D7E5C406B0B7492528D3640	f	812714b9-873b-41b9-b849-acb601551000	\N
61bcbb6a-3d64-4fee-8556-13eed412b2e6	Artisans	Establishment, food	Рейтинг Google: 4.6 (10 отзывов). Адрес: GW8Q+QP7, Nanyou, Nanshan, Shenzhen, Guangdong Province, Китай, 518064	0101000020E6100000151F9F901D7C5C4010165FFE54843640	f	812714b9-873b-41b9-b849-acb601551000	\N
e7c39ea8-2c25-49e9-b89b-e0f004c39584	Кофейня LN Fortunate	Establishment, food	Рейтинг Google: 4.4 (429 отзывов). Адрес: Гонконг, 西營盤第二街118號懿山地舖	0101000020E61000008610A15BF9885C404BC0F91E3F493640	f	812714b9-873b-41b9-b849-acb601551000	\N
32f6fc00-182c-4a78-8cce-9dbf95b93376	静颐茶馆	Establishment, point of interest	Рейтинг Google: 4.6 (27 отзывов). Адрес: Luohu District, Шэньчжэнь, Китай, 518022	0101000020E6100000FFB1101D02875C40BD18CA89768D3640	f	812714b9-873b-41b9-b849-acb601551000	\N
22039e8e-f2bf-4a4b-8552-7ed4fa87d30e	鼎泰丰	Establishment, food	Рейтинг Google: 4 (28 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 地王 Bao An Nan Lu, 1881号, Wan Xiang Cheng 3楼	0101000020E6100000112C58F418875C40BEE435655D8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
e3e386ef-1535-4288-b31b-52f3e6e25b8c	麦考利	Establishment, food	Рейтинг Google: 4.4 (12 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, Nanyou, Tai Zi Lu, 海上世界广场118号 邮政编码: 518060	0101000020E6100000AC1BEF8E8C7A5C409609BFD4CF7B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
42dd7b3c-e2a5-41d3-ba9d-2c00de1017e1	Altitude	Bar, establishment	Рейтинг Google: 4.8 (5 отзывов). Адрес: G3M4+P44中心城 Futian District, Шэньчжэнь, Гуандун, Китай, 518046	0101000020E610000060E39FBE8A835C4006A2821EC5883640	f	812714b9-873b-41b9-b849-acb601551000	\N
01791b52-4efc-46cd-ac34-e9b8b73ede26	Mevlana Turkish Restaurant	Establishment, food	Рейтинг Google: 4.2 (452 отзывов). Адрес: 154 Zhen Xing Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518020	0101000020E61000000CAD4ECE50855C40C05B2041F18B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
9f5a5022-c94a-47de-9818-71ba2743cfb1	George and Dragon British Pub	Establishment, food	Рейтинг Google: 4.2 (17 отзывов). Адрес: 7 Tai Zi Lu, 蛇口 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518060	0101000020E6100000363003DF7E7A5C40A941E268D87B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
4299ae7b-3782-40d6-99f7-d7e77910a1b7	The Oct Harbour, Shenzhen - Marriott Executive Apartments	Establishment, lodging	Рейтинг Google: 4.4 (359 отзывов). Адрес: No 8 East Baishi Road The OCT Harbour, 南山区深圳市 Китай, 518053	0101000020E6100000C631923D427F5C40D9E9077591863640	f	812714b9-873b-41b9-b849-acb601551000	\N
f1da82df-454d-4c01-a3e0-bc7d76f8f3bb	O'Vamos	Establishment, food	Рейтинг Google: 5 (2 отзывов). Адрес: Китай, Shen Zhen Shi, Nan Shan Qu, CN 广东省 深圳市 南山区 白石路 1 层 邮政编码: 518053	0101000020E61000008FDFDBF4677F5C40AD69DE718A863640	f	812714b9-873b-41b9-b849-acb601551000	\N
18fb986f-40c4-41ef-ba31-9f42a2d59d6d	Coco Park Bar Street	Establishment, point of interest	Рейтинг Google: 4.6 (14 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 福田ＣＢＤ中心二路G3M3+CWW 邮政编码: 518017	0101000020E61000009488F02F82835C402EC901BB9A883640	f	812714b9-873b-41b9-b849-acb601551000	\N
c95cf007-c592-43f4-92d8-74adb323ffc4	探魚	Establishment, food	Рейтинг Google: 4.4 (15 отзывов). Адрес: Китай, 广东省深圳市罗湖区地王G4Q6+W7G 邮政编码: 518000	0101000020E61000000700D8CA15875C402E347CB0318A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
6b5a97a2-eb51-4c25-bcb8-fa4c7f9fc480	星河·COCOPARK酒吧街	Bar, establishment	Рейтинг Google: 4.6 (9 отзывов). Адрес: G3M3+CW2中心城 Futian District, Shenzhen, Guangdong Province, Китай, 518017	0101000020E61000003B71395E81835C407F6ABC7493883640	f	812714b9-873b-41b9-b849-acb601551000	\N
f931c974-d1d7-4569-9c96-cd9820a428c9	俄罗斯风味	Establishment, food	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 笋岗东路 邮政编码: 518023	0101000020E61000008A20CEC309875C4067D5E76A2B8E3640	f	812714b9-873b-41b9-b849-acb601551000	\N
af94bbc6-5c06-4419-ad8e-9c1259a952ee	Backerei Thomas	Bakery, establishment	Рейтинг Google: 5 (3 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, 南头 Hong Hua Lu, 南山豪庭112号 邮政编码: 518056	0101000020E6100000F6E34059C27A5C40287CB60E0E8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
31e7ade0-aef8-4c08-b334-b6580e68023f	Beeplus Lifestyle	Bakery, establishment	Рейтинг Google: 4.5 (11 отзывов). Адрес: GW9Q+3M4, Hai De San Dao, Nanyou, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518064	0101000020E61000008681F80A1C7C5C40E195C91583843640	f	812714b9-873b-41b9-b849-acb601551000	\N
d80c0139-dc4c-47f1-9310-12a534eda1f4	满记甜品	Bakery, establishment	Рейтинг Google: 3.6 (8 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 中心城福华路星河Coco Park B1-073B号（近民田路口） 邮政编码: 518046	0101000020E6100000DDCD531D72835C4055DCB8C5FC883640	f	812714b9-873b-41b9-b849-acb601551000	\N
17069230-dfe1-427f-a1c3-1f89abc14fd4	Honeymoon Dessert	Establishment, food	Рейтинг Google: 4.5 (2 отзывов). Адрес: 9028 Shen Nan Da Dao, 华侨城 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518053	0101000020E610000061A351265A7E5C40B4661A03A1893640	f	812714b9-873b-41b9-b849-acb601551000	\N
72ab778e-94b5-4532-9b9f-993a11fbba30	幸福西饼	Bakery, establishment	Рейтинг Google: 5 (1 отзывов). Адрес: GXMV+C6W, Shen Nan Da Dao, 华侨城 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518053	0101000020E6100000B1BBE58F8E7F5C40D47D00529B883640	f	812714b9-873b-41b9-b849-acb601551000	\N
0b1ced7f-eaa7-43ac-8a0e-998ff9e19db1	The Mandarin Cake Shop - Mandarin Oriental, Shenzhen	Bakery, establishment	Рейтинг Google: Нет оценки (0 отзывов). Адрес: A座, 2楼, 深业上城, 5001 Huang Gang Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518026	0101000020E610000034524A638F845C40A12FBDFDB98E3640	f	812714b9-873b-41b9-b849-acb601551000	\N
9424f07f-c94e-4309-96ba-89a101f15123	可颂坊	Bakery, establishment	Рейтинг Google: 4 (1 отзывов). Адрес: GXP3+GHV, Gao Xin Nan Si Dao, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518058	0101000020E61000008E75711B0D7D5C401F0A0B934E893640	f	812714b9-873b-41b9-b849-acb601551000	\N
ae9c52a4-d173-44a0-bba2-9d44d48c9d1d	Baker Tang	Bakery, establishment	Рейтинг Google: Нет оценки (0 отзывов). Адрес: 32 Bai Hua Er Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518028	0101000020E61000002187D228EE855C401FDB32E02C8D3640	f	812714b9-873b-41b9-b849-acb601551000	\N
ce80f2a6-74b0-4573-8a49-cb53f64bef48	Honey Moon Dessert	Bakery, establishment	Рейтинг Google: Нет оценки (0 отзывов). Адрес: G4RG+QPW, Chun Feng Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай	0101000020E610000056AF6C301E885C4009168733BF8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
30b293c1-475d-4338-8634-6ebcad9000be	Lola Western-style Cake Mill	Bakery, establishment	Рейтинг Google: Нет оценки (0 отзывов). Адрес: FWPG+C4C, She Kou Lao Jie, Nanyou, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518060	0101000020E6100000B47570B0377B5C40159161156F7C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
271dfdc3-9f3d-4a84-8d47-2ce329dda47e	Holiland	Establishment, food	Рейтинг Google: 4.3 (3 отзывов). Адрес: HW63+6W8, Xin Zhen Xi Lu, Bao An Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518133	0101000020E610000071395E81E8795C4030116F9D7F8F3640	f	812714b9-873b-41b9-b849-acb601551000	\N
39d3a9c7-18f6-4584-a152-7a748f4bc4e2	Happiness Cake	Bakery, establishment	Рейтинг Google: Нет оценки (0 отзывов). Адрес: 1006-35 Chuang Ye Yi Lu, 1006, Bao An Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518133	0101000020E6100000A245B6F3FD785C402D211FF46C8E3640	f	812714b9-873b-41b9-b849-acb601551000	\N
a029946a-fd79-4595-a16f-9f243a9348b7	Songxiaobei	Bakery, establishment	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, 18, 正南方向50米 邮政编码: 518063	0101000020E6100000F60F7DD2E47C5C409BE21698BA8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
ba67dc5c-fe76-4109-b163-c48649623b71	坳下市场	Establishment, point of interest	Рейтинг Google: 2 (4 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, Liantang, 坳下村	0101000020E610000002284696CC8A5C4060CC96AC8A903640	f	812714b9-873b-41b9-b849-acb601551000	\N
254f4373-c449-4eb6-82c6-c25d0b88833c	深圳古玩城	Establishment, home goods store	Рейтинг Google: 3.8 (13 отзывов). Адрес: Luohu District, Шэньчжэнь, Китай	0101000020E6100000179CC1DF2F895C408F17D2E1218C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
b77cdedf-a976-4003-8c75-3e1c9dc0f3cb	The Brew Shenzhen	Bar, establishment	Рейтинг Google: 4.1 (31 отзывов). Адрес: Китай, 广东省深圳市福田区福田ＣＢＤG3M5+QV5 邮政编码: 518046	0101000020E6100000173B2BB3D2835C40BB192433CD883640	f	812714b9-873b-41b9-b849-acb601551000	\N
b5e73ca3-c492-4a6b-b4f4-fdf5dd188609	Xpats	Bar, establishment	Рейтинг Google: 3.8 (22 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 中心城 Fu Hua Yi Lu, 3号怡景中心城1层 邮政编码: 518046	0101000020E6100000A05225CADE835C400CB08F4E5D893640	f	812714b9-873b-41b9-b849-acb601551000	\N
7169319a-14ea-4c8a-916c-f336e86456a1	George and Dragon Pub	Bar, establishment	Рейтинг Google: 5 (7 отзывов). Адрес: 3 Tai Zi Lu, 蛇口 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518060	0101000020E61000004811BE9C7E7A5C4074513E4EE27B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
e5fe3032-f22e-4760-baba-3a5c9939c7df	Zazoo	Bar, establishment	Рейтинг Google: 5 (12 отзывов). Адрес: Китай, 区 Fu Tian Qu, 中心城 Gou Wu Gong Yuan Di Tie Shang Ye Jie, C CN 广东省 深圳市 邮政编码: 518046	0101000020E61000002CBCCB457C835C40E2AFC91AF5883640	f	812714b9-873b-41b9-b849-acb601551000	\N
12f45107-7ce2-447b-98c3-99505c63a5a0	Frankie's	Bar, establishment	Рейтинг Google: 4.5 (15 отзывов). Адрес: 288 Rong Hua Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518042	0101000020E6100000D7A3703D0A835C40F1E1485634823640	f	812714b9-873b-41b9-b849-acb601551000	\N
4db4e5e2-ea87-4512-8ce3-b48cb4850a7e	Garden Pub	Bar, establishment	Рейтинг Google: 2.5 (2 отзывов). Адрес: 5 Guihua Rd, Mai Po, Китай	0101000020E61000006E693524EE835C4017F19D98F5823640	f	812714b9-873b-41b9-b849-acb601551000	\N
982872b4-d56a-450c-be0b-8fbdec992a93	Lili Marleen	Bar, establishment	Рейтинг Google: 4 (8 отзывов). Адрес: 138 Min Tian Lu, 中心城 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518046	0101000020E61000003D5AE6BE66835C40480E2263FF883640	f	812714b9-873b-41b9-b849-acb601551000	\N
a3752226-2d57-4bd9-86e7-6d27103824cf	艾莉酒吧餐廳 Aili Bar & Restaurant	Bar, establishment	Рейтинг Google: 5 (1 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, Huang Gang Gong Yuan Yi Jie, 水圍村146棟地下 邮政编码: 518038	0101000020E6100000BF9767CAF3835C407C201E2EDE843640	f	812714b9-873b-41b9-b849-acb601551000	\N
b191cdc1-cf65-4cd8-9368-1d2ca5114efe	Open Air Music Pub	Bar, establishment	Рейтинг Google: 4 (1 отзывов). Адрес: G3P3+JG4, Fu Hua Yi Lu, 福田ＣＢＤ Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518046	0101000020E61000001900AAB871835C403E74E6C358893640	f	812714b9-873b-41b9-b849-acb601551000	\N
6b41a38f-8951-430f-902a-fcfae011d2c7	麦考利爱尔兰酒吧	Bar, establishment	Рейтинг Google: 3.9 (42 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 中心城 Min Tian Lu, 138号购物公园151-152号 邮政编码: 518046	0101000020E6100000930035B56C835C408ACC5CE0F2883640	f	812714b9-873b-41b9-b849-acb601551000	\N
e5010d44-1b57-4b84-96c0-2a888cb9e281	Maotouying Caimei Pub	Bar, establishment	Рейтинг Google: 5 (1 отзывов). Адрес: G4M9+Q23, Jianshe Rd, Closed Area, Китай	0101000020E6100000C28A53AD85875C40793E03EACD883640	f	812714b9-873b-41b9-b849-acb601551000	\N
e6fee9d7-6f78-4682-87bc-da5d2ff3aabd	La Vie Club	Bar, establishment	Рейтинг Google: 5 (3 отзывов). Адрес: G3P3+57P, Min Tian Lu, 福田ＣＢＤ Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518046	0101000020E6100000DD37088467835C400E6ABFB513893640	f	812714b9-873b-41b9-b849-acb601551000	\N
4094fc07-070d-4ae3-9f24-ec2aac45b63a	Viva Club	Bar, establishment	Рейтинг Google: 3.9 (82 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 中心城 Fu Hua Lu, 福华路城建购物公园140号 邮政编码: 518046	0101000020E6100000554CA59F70835C40AE6186C613893640	f	812714b9-873b-41b9-b849-acb601551000	\N
7755af1d-0125-488b-8ef0-92b3997fd890	Fans Bar Pub	Bar, establishment	Рейтинг Google: 5 (1 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, Fu Ming Lu, 福明路嘉汇新城6层 邮政编码: 518039	0101000020E610000098C1189128855C40CE548847E2893640	f	812714b9-873b-41b9-b849-acb601551000	\N
c7c39355-7d5b-4110-8524-f742b4b26a24	Mowang Pub	Bar, establishment	Рейтинг Google: 3.5 (2 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 福田ＣＢＤ Fu Hua San Lu, 268号085-087室 邮政编码: 518048	0101000020E6100000246651337F835C40E28F47156A883640	f	812714b9-873b-41b9-b849-acb601551000	\N
0094ef88-6819-4fcf-9b9a-a2d5bbaf3048	Shopping Park Pub Music Square	Bar, establishment	Рейтинг Google: 4.3 (3 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 中心城 Min Tian Lu, 138号购物公园北园 邮政编码: 518046	0101000020E6100000F92D3A596A835C40A9FB00A436893640	f	812714b9-873b-41b9-b849-acb601551000	\N
6b7568c8-ae1e-4007-92bb-b328a97433b0	E.T. Brewery精酿啤酒工厂	Bar, establishment	Рейтинг Google: 4.1 (37 отзывов). Адрес: 60 Hai De San Dao, 后海 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518054	0101000020E6100000F89F466BD67B5C40E63E390A10853640	f	812714b9-873b-41b9-b849-acb601551000	\N
4e2cbc96-caff-4b49-81d7-8a10c97e0f8f	Bionic Brew Taproom	Bar, establishment	Рейтинг Google: 3 (3 отзывов). Адрес: GXW9+FG4, Nanshan, Шэньчжэнь, Гуандун, Китай, 518072	0101000020E61000005FA6DC33017E5C40FB16E7B9CF8B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
72743fd5-8ad9-4c31-b05b-a31e455b42a9	Craft Head	Bar, establishment	Рейтинг Google: 5 (10 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Second Floor Xin Zhou Er Jie, and CN 新洲七街 邮政编码: 518000	0101000020E6100000810E4E9FF8825C40E0E5D830F9853640	f	812714b9-873b-41b9-b849-acb601551000	\N
a061a221-60e1-483e-8ed4-c754eb3c8c23	Half Ton Brewery (Chegongmiao Br)	Establishment, food	Рейтинг Google: 4 (6 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, Tai Ran Si Lu, 212-1号层106 邮政编码: 518042	0101000020E61000008109DCBA9B815C409C8A54185B883640	f	812714b9-873b-41b9-b849-acb601551000	\N
d26572cc-42b4-4cd7-b8cb-5e3496ff5982	Rich Kat	Bar, establishment	Рейтинг Google: 3.5 (12 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, 163, 正东方向40米 邮政编码: 518060	0101000020E61000001A69A9BC1D7B5C403D0AD7A3707D3640	f	812714b9-873b-41b9-b849-acb601551000	\N
fb440826-081f-41af-be1c-e70c2dda8290	Shenzhen Kingway Brewery Co.,Ltd.	Establishment, point of interest	Рейтинг Google: Нет оценки (0 отзывов). Адрес: H4GP+75H, Dong Chang Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518019	0101000020E6100000257090B5AB885C4081785DBF60933640	f	812714b9-873b-41b9-b849-acb601551000	\N
d0c7d917-0fc0-41db-91b4-75e7c7974dc7	The Peat	Bar, establishment	Рейтинг Google: 4.8 (14 отзывов). Адрес: G2JC+6WJ, Futian District, Shenzhen, Guangdong Province, Китай, 518041	0101000020E6100000AB2BFA9E6C815C40BD5C1F31D5873640	f	812714b9-873b-41b9-b849-acb601551000	\N
60ea5680-e60c-43b9-b74b-f7185c6d1257	Bar Demon 78-79	Bar, establishment	Рейтинг Google: 4.1 (7 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 福田ＣＢＤ中心二路G3M3+HR4 邮政编码: 518046	0101000020E6100000D7135D177E835C4036902E36AD883640	f	812714b9-873b-41b9-b849-acb601551000	\N
61e7daba-e6f9-46e3-b008-c9d476f4c6c9	Fannou House	Bar, establishment	Рейтинг Google: 4.5 (4 отзывов). Адрес: GXRQ+W2Q, Nanshan, Шэньчжэнь, Гуандун, Китай, 518074	0101000020E610000014596B28357F5C405C06F75ED78A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
f47ce25b-91de-4082-8e79-e32693a4ed52	Demon Bar	Bar, establishment	Рейтинг Google: 4 (1 отзывов). Адрес: Китай, Shen Zhen Shi, Fu Tian Qu, CN 广东省 深圳市 福田区 KKONEL134 134A 邮政编码: 518042	0101000020E610000039B4C876BE815C4090831266DA863640	f	812714b9-873b-41b9-b849-acb601551000	\N
873c0c51-0436-4081-bdd6-0495abddb78b	The Compass Bar	Bar, establishment	Рейтинг Google: Нет оценки (0 отзывов). Адрес: 4002 Jin Tian Lu, 中心城 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518017	0101000020E6100000CBF8F71917845C40397F130A11883640	f	812714b9-873b-41b9-b849-acb601551000	\N
e0b5ded5-26c4-44f6-8458-c66e3e4f2585	Superface Club	Establishment, night club	Рейтинг Google: 4.2 (5 отзывов). Адрес: 1 Xing Nan Lu, Nanyou, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518066	0101000020E6100000970D219D707B5C40C3D5011077813640	f	812714b9-873b-41b9-b849-acb601551000	\N
2f458f9a-29a4-42b0-befa-b49d604e582e	Xingguangcheng	Establishment, night club	Рейтинг Google: 5 (3 отзывов). Адрес: M53X+FP9, Xing Wang Lu, Long Gang Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518115	0101000020E610000043989130C28C5C406F6017EA55A73640	f	812714b9-873b-41b9-b849-acb601551000	\N
d379d89f-6d65-44f1-81c3-a90b58c02620	Pepper Club	Bar, establishment	Рейтинг Google: 4 (15 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 中心城中心二路购物公园2层 邮政编码: 518046	0101000020E6100000EACC3D247C835C405DA3E5400F893640	f	812714b9-873b-41b9-b849-acb601551000	\N
4a1309e3-1704-4086-ac96-aab4d0341c50	Xinglong Night Club	Establishment, night club	Рейтинг Google: 5 (1 отзывов). Адрес: 2086 Hong Gui Lu, 蔡屋围 Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518001	0101000020E61000004C8DD0CFD4865C4070B1A206D38C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
ac841766-9a00-4fed-895a-b28afb285a21	Qunxing Night Club	Establishment, night club	Рейтинг Google: 3.6 (5 отзывов). Адрес: 118 Zhen Hua Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518037	0101000020E6100000533F6F2A52855C40556CCCEB888B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
c8a53b48-b93e-4f19-ac5e-e7f39207b6f1	Chocolate	Establishment, night club	Рейтинг Google: 5 (2 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 永新路G4V8+PWH 邮政编码: 518010	0101000020E6100000D5EAABAB82875C40DF5740FC578B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
efea1db6-d929-4c04-98c1-cdc3379f4a58	Face	Bar, establishment	Рейтинг Google: 4.4 (7 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, Bao An Nan Lu, 1881号万象城2期4层	0101000020E6100000F48B12F417875C40B3D1393FC5893640	f	812714b9-873b-41b9-b849-acb601551000	\N
f132a5ce-fdc5-4df0-97d9-2f24ff841319	MOJO Club	Establishment, night club	Рейтинг Google: 3.5 (4 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 福田ＣＢＤ中心二路139号 邮政编码: 518000	0101000020E6100000D35FF93D7B835C408DA9054026893640	f	812714b9-873b-41b9-b849-acb601551000	\N
a2868160-b079-414f-b115-a5675d41e196	Lasiweijia Si Night Club	Establishment, night club	Рейтинг Google: 4 (5 отзывов). Адрес: 5022 Bin He Da Dao, 岗厦 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518016	0101000020E6100000147AFD497C845C40D767CEFA94873640	f	812714b9-873b-41b9-b849-acb601551000	\N
ead70ae3-09b0-44bd-9e37-b633af032d13	Feicui Mingzhu Club	Establishment, night club	Рейтинг Google: 4.5 (2 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, Chun Feng Lu, 1号新都酒店4-6层	0101000020E610000097A949F086875C40963FDF162C893640	f	812714b9-873b-41b9-b849-acb601551000	\N
4c8a9c99-779e-4277-a0c9-0977b2a21324	Solo Club	Bar, establishment	Рейтинг Google: 3.5 (6 отзывов). Адрес: Китай, Shen Zhen Shi, Fu Tian Qu, 中心城北园 CN 广东省 深圳市 福田区 民田路购物公园 邮政编码: 518046	0101000020E6100000C85EEFFE78835C4062156F641E893640	f	812714b9-873b-41b9-b849-acb601551000	\N
4e8c1aef-ef1c-457f-b1c0-ef640c2b22fa	Taipingshengshi Night Club	Establishment, night club	Рейтинг Google: 5 (1 отзывов). Адрес: P7J4+Q54, Min Sheng Lu, 龙岗中心城 Long Gang Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518172	0101000020E6100000EA72EF8659905C40AD4B32175DBB3640	f	812714b9-873b-41b9-b849-acb601551000	\N
24c56f12-c2d7-466d-a8c2-fb4d784b4fa3	Lefuhao Night Club	Establishment, night club	Рейтинг Google: 4 (1 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, Zhen Hua Lu, 苏发大厦305栋 邮政编码: 518028	0101000020E610000090430E5BC4855C40ED7F80B56A8B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
6226bcd9-538a-491f-9e9c-477eb0d1b62f	Jinzun Entertainment Club	Establishment, night club	Рейтинг Google: 5 (1 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Long Hua Qu, 152, Guan Lan Da Dao, 152号诺诚大酒店 邮政编码: 518110	0101000020E610000086032159C0825C40FFB27BF2B0B03640	f	812714b9-873b-41b9-b849-acb601551000	\N
950f11b6-fb9d-4236-a8a6-d14db5425bdd	Penny Black Jazz Cafe	Establishment, point of interest	Рейтинг Google: 4.6 (7 отзывов). Адрес: Wen Chang Jie, 华侨城 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518074	0101000020E61000002A430BBF8A7F5C4099D30A783E8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
2afd1b34-abc2-4f24-8f9a-4de575cbd66c	Jazz Garden	Bar, establishment	Рейтинг Google: 3.7 (3 отзывов). Адрес: GXPF+64C, Shen Nan Da Dao, 华侨城 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518058	0101000020E61000009751D1FD417E5C404C55DAE21A893640	f	812714b9-873b-41b9-b849-acb601551000	\N
b0764f80-c556-4802-a2b4-35320bb995ee	Meeting Jazz Club	Bar, establishment	Рейтинг Google: 3 (2 отзывов). Адрес: Китай, 广东省深圳市南山区蛇口FWP8+JRF 邮政编码: 518060	0101000020E610000029ED0DBEB07A5C4046C0D7C68E7C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
5be07ae7-4660-4408-b3b3-53c37059ea42	Jueshi Club	Establishment, night club	Рейтинг Google: Нет оценки (0 отзывов). Адрес: 1028 Hong Ling Zhong Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518022	0101000020E61000000E68E90AB6865C4008E412471E8C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
329e89de-0628-4e73-a2fb-da0faf2c079b	Luohu Commercial City	Establishment, point of interest	Рейтинг Google: 3.7 (565 отзывов). Адрес: Closed Area, Гонконг	0101000020E61000007714E7A8A3875C401D3D7E6FD3873640	f	812714b9-873b-41b9-b849-acb601551000	\N
232dca4a-65bf-4d75-a598-debde6fe4bc5	金光华广场	Establishment, point of interest	Рейтинг Google: 4.1 (284 отзывов). Адрес: 2028 Ren Min Nan Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай	0101000020E6100000E78A5242B0875C40DE1CAED51E8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
cbe4a045-888a-49a3-8577-2a27256da760	壹方城購物中心	Establishment, point of interest	Рейтинг Google: 4.4 (142 отзывов). Адрес: HV2Q+W3V, Baoan, Shenzhen, Guangdong Province, Китай, 518052	0101000020E610000090EDC6CCCF785C40FB39AA3F678D3640	f	812714b9-873b-41b9-b849-acb601551000	\N
48328bbd-a60f-4dee-9322-c88d7e5ce813	Haiya Mega Mall	Establishment, point of interest	Рейтинг Google: 3.9 (59 отзывов). Адрес: 2746 Nan Hai Da Dao, Nanyou, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518054	0101000020E6100000DBFD2AC0777B5C40C0CDE2C5C2843640	f	812714b9-873b-41b9-b849-acb601551000	\N
6067eea3-0456-4505-994a-e4e93b14e1b6	观澜湖新城MH MALL	Establishment, point of interest	Рейтинг Google: 4.5 (35 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Long Hua Qu, Gao Er Fu Da Dao, 8号邮政编码: 邮政编码: 518111	0101000020E6100000991FC9F66B855C405AF624B039B93640	f	812714b9-873b-41b9-b849-acb601551000	\N
85630128-2fe5-43f8-84ce-0dc8b78a6978	深圳灣萬象城	Establishment, point of interest	Рейтинг Google: 4.2 (91 отзывов). Адрес: GW8W+GMR, Nanshan, Shenzhen, Guangdong Province, Китай, 518064	0101000020E61000008421BC87957C5C408E70FF3630843640	f	812714b9-873b-41b9-b849-acb601551000	\N
b630ff50-3031-436e-92e3-4c0488ab4a75	World Trade Center	Establishment, point of interest	Рейтинг Google: 3.2 (5 отзывов). Адрес: P68W+VCH, Long Xiang Da Dao, 龙岗中心城 Long Gang Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518172	0101000020E6100000AFB0E07EC08F5C40E736E15E99B73640	f	812714b9-873b-41b9-b849-acb601551000	\N
ecd23941-0ffc-4191-b64b-bed50874a2d5	Seg Electronics Market	Electronics store, establishment	Рейтинг Google: 4.5 (402 отзывов). Адрес: Futian District, Шэньчжэнь, Китай, 518039	0101000020E6100000A9177C9A93855C404F0306499F8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
cd60fc35-9fcc-421e-9895-47e2f2179514	Shekou Market	Establishment, point of interest	Рейтинг Google: 3.9 (45 отзывов). Адрес: FWPH+F85, Yu Cun Nan Lu, Nanyou, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518060	0101000020E610000005DCF3FC697B5C40D7C22CB4737C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
204a7454-3784-425b-922e-86a4897cd4f8	Shenzhen Books And Magazines Wholesale Market	Establishment, point of interest	Рейтинг Google: 4.2 (6 отзывов). Адрес: 33 Ba Gua Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518029	0101000020E6100000E1CE85915E865C40AB21718FA58F3640	f	812714b9-873b-41b9-b849-acb601551000	\N
d6e4f6ae-be51-4ddf-864d-894a19ae61a6	Huaqiangbei Commercial Street	Establishment, point of interest	Рейтинг Google: 4.5 (113 отзывов). Адрес: G3RP+9MG, Hua Qiang Bei Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518000	0101000020E61000003BA8C4758C855C404AEF1B5F7B8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
a0810251-db96-4ff6-b7b8-151d47c4f325	Xihua Palace Shopping Center	Establishment, point of interest	Рейтинг Google: 3.9 (35 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 东门步行街G4W9+C4H 邮政编码: 518001	0101000020E61000009BFB500E8B875C40AAB46A7CCB8B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
17074173-ea05-4981-8003-cec196ef0e04	华侨城创意文化园T街创意市集	Establishment, point of interest	Рейтинг Google: 3.9 (82 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, 恩平路GXPV+W6F 邮政编码: 518053	0101000020E61000007C7A11128E7F5C407D9752978C893640	f	812714b9-873b-41b9-b849-acb601551000	\N
f1b18bcc-4bc6-47b0-b24f-16272593e5da	Sed Electronic Communication Market	Electronics store, establishment	Рейтинг Google: 3.7 (14 отзывов). Адрес: 46 Hua Fa Bei Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518028	0101000020E610000065170CAEB9855C407BD80B056C8B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
7a17e3a8-543f-428e-a58d-61edfbbf63a0	Jiahua Foreign Trade Clothing Market	Establishment, point of interest	Рейтинг Google: 3.4 (11 отзывов). Адрес: 2007 Hua Qiang Bei Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518028	0101000020E6100000C05E61C17D855C401F871CB6888B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
6e4480a0-b912-4ae3-b83c-50b6e4846f62	Tongtiandi Telecommunication Market	Establishment, point of interest	Рейтинг Google: 2.2 (18 отзывов). Адрес: 2071 Shen Nan Zhong Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518027	0101000020E610000001BD70E7C2855C40A7B393C1518A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
b1710d6d-c417-49ec-80db-bc1e5b0da9a4	Shenzhen SEG Electronics Market Aifa Exhibition And Marketing Department	Establishment, point of interest	Рейтинг Google: 4.6 (45 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, Shen Nan Zhong Lu, 3039号深圳国际文化大厦 邮政编码: 518039	0101000020E61000002DB1321AF9845C4099BB96900F8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
caaa1950-27c3-4ac4-8160-ee743ff4f41c	Shenzhen Gift	Establishment, point of interest	Рейтинг Google: 5 (1 отзывов). Адрес: 9037 Shen Nan Da Dao, 9037, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518058	0101000020E6100000EE5F5969527E5C40F085C954C1883640	f	812714b9-873b-41b9-b849-acb601551000	\N
cc5435c3-7c53-4109-aa30-7ee352d38f81	Panda Souvenir Store	Establishment, point of interest	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Китай, 内 Nan Shan Qu, 4065, Xi Li Hu Lu, 4065号, Shen Zhen Ye Sheng Dong Wu Yuan CN 广东省 深圳市 邮政编码: 518071	0101000020E6100000431CEBE2367E5C40A835CD3B4E993640	f	812714b9-873b-41b9-b849-acb601551000	\N
e20b7fe1-4f7b-42a0-a40b-144b6cfbf7e5	Shenzhen Clocks And Watches Peitao Market	Establishment, point of interest	Рейтинг Google: 4.2 (48 отзывов). Адрес: 148 Zhen Xing Lu, 曼哈商业广场 Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518037	0101000020E610000044F8174163855C406CCD565EF28B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
eb60d7bc-362e-4531-b2d9-c2d4fbd2f1f6	Антикварный маркет "Блошинка"	Establishment, home goods store	Рейтинг Google: 4.4 (14 отзывов). Адрес: Большой Овчинниковский пер., 24, стр. 4, Москва, Россия, 115184	0101000020E61000002CA3EC889ED0424042EBE1CB44DF4B40	f	812714b9-873b-41b9-b849-acb601551000	\N
383af59b-b8a1-46cb-ba25-68c08e27dd04	Shajing Market	Establishment, point of interest	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Bao An Qu, 白龙商业步行街PR9V+P9M 邮政编码: 518105	0101000020E61000006E6C76A4FA755C4081CD397826B83640	f	812714b9-873b-41b9-b849-acb601551000	\N
c25dbe1b-7645-4e8e-ae06-7d3e82345534	Nanyou Fashionable Dress Wholesale Center	Clothing store, establishment	Рейтинг Google: 4.3 (11 отзывов). Адрес: GW5F+JXG, Nan Hai Da Dao, Nanyou, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518064	0101000020E610000022E2E654327B5C405F07CE1951823640	f	812714b9-873b-41b9-b849-acb601551000	\N
9341cef8-044c-4395-9759-b6295aafc8e6	9 Square	Establishment, point of interest	Рейтинг Google: 4.3 (35 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, 宝安区人民路2020号 邮政编码: 518131	0101000020E610000054909F8D5C815C40C93D5DDDB1A03640	f	812714b9-873b-41b9-b849-acb601551000	\N
a00fcf22-9cbf-4d71-a2c2-596b01a512b7	Monki	Clothing store, establishment	Рейтинг Google: Нет оценки (0 отзывов). Адрес: 269 Fu Hua San Lu, 福田ＣＢＤ Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518048	0101000020E610000005DF347D76835C40CD94D6DF12883640	f	812714b9-873b-41b9-b849-acb601551000	\N
e0ebe77a-94e3-47c4-9195-cb3bbc364991	Shenzhen Tourism Bureau	Establishment, point of interest	Рейтинг Google: 1 (1 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 中心城 Fu Zhong San Lu, 市民中心行政服务大厅西53 邮政编码: 518000	0101000020E6100000DB334B02D4835C40807F4A95288B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
3259b3d9-6717-410d-ab5a-970ae8e149d6	深圳旅游咨询中心	Establishment, point of interest	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 上步北路 邮政编码: 518035	0101000020E61000005648F949B5855C403E20D099B4913640	f	812714b9-873b-41b9-b849-acb601551000	\N
b021b6e4-f43e-49c1-9ad6-c1097a20b60f	深圳市民中心	Establishment, point of interest	Рейтинг Google: 4.6 (22 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 中心城深南大道 邮政编码: 518000	0101000020E6100000ACFD9DEDD1835C401E335019FF8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
8741eae5-efab-4cfb-989a-880290da59e2	Cits	Establishment, point of interest	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Fu Jian Da Sha B Zuo, 14层2048 Cai Tian Lu, 2048, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518038	0101000020E610000046B1DCD26A845C40C616821C94883640	f	812714b9-873b-41b9-b849-acb601551000	\N
872f4c4a-c717-42fb-b4ca-0845d806f7a9	Foreign Currency Exchange Wang	Bank, establishment	Рейтинг Google: 5 (2 отзывов). Адрес: 4068-9 Yi Tian Lu, 4068, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518046	0101000020E6100000C8D2872EA8835C40A9BC1DE1B4883640	f	812714b9-873b-41b9-b849-acb601551000	\N
9c9188d6-3866-429e-aec1-c05d6639e2d5	Bank Of China Foreign Currency Exchange	Bank, establishment	Рейтинг Google: 5 (2 отзывов). Адрес: GW9P+WV3, Wen Xin Wu Lu, 后海 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518054	0101000020E610000080D767CEFA7B5C4081C17F040F853640	f	812714b9-873b-41b9-b849-acb601551000	\N
97bfb444-a2c1-49e6-a1d2-6511117c5d68	United Money	Establishment, finance	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 中心城 Shen Nan Da Dao, 4019号-3 邮政编码: 518046	0101000020E6100000B77F65A549835C40AA61BF27D6893640	f	812714b9-873b-41b9-b849-acb601551000	\N
bc142b85-47b2-4977-9811-2b8bc19f81db	同仁堂	Establishment, health	Рейтинг Google: 3.3 (3 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 建设路1072号-1	0101000020E6100000179B560A81875C40925ED4EE57893640	f	812714b9-873b-41b9-b849-acb601551000	\N
d8c9fb7b-fa96-4ea4-8995-0d2c68df85c8	Ershi No.4 Primary Sch. Shiyaofang	Establishment, health	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Bao An Qu, 61, 东北方向70米 邮政编码: 518108	0101000020E6100000FDBCA948857B5C40BDFBE3BD6AAD3640	f	812714b9-873b-41b9-b849-acb601551000	\N
4c1c9fdc-5115-479c-854c-2e14858208cd	BEST Convenience Store	Convenience store, establishment	Рейтинг Google: Нет оценки (0 отзывов). Адрес: 101 Tai Ning Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518020	0101000020E6100000B14170A6D3885C403A9160AA99913640	f	812714b9-873b-41b9-b849-acb601551000	\N
fe135799-e21a-418b-a7bb-1b1b2737652d	Best Convenience Store	Establishment, food	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, Tang Yan Qi Jie, 上沙塘晏村七巷11-2 邮政编码: 518042	0101000020E6100000CE3637A627825C40BB9866BAD7853640	f	812714b9-873b-41b9-b849-acb601551000	\N
eafb100e-7812-4906-b3e8-b996d28d0f48	KANGCHENG MEDICAL SHENZHEN CO., LTD.	Establishment, point of interest	Рейтинг Google: Нет оценки (0 отзывов). Адрес: No 33, Dongfang Road, Songgang Street, 宝安区深圳市广东省 Китай, 518105	0101000020E610000048156AF239775C406FD8B628B3C13640	f	812714b9-873b-41b9-b849-acb601551000	\N
02c08188-4b70-4e96-9e5f-ac6d1dd1449f	Zhonggang Large Pharmacy	Establishment, health	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 中兴路88号-1 邮政编码: 518001	0101000020E6100000FA7FD59123885C40DD611399B98C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
8f1db4d0-d307-4f12-8686-6f71a76100b6	Beijing Tongrentang Hubei Shop	Establishment, point of interest	Рейтинг Google: Нет оценки (0 отзывов). Адрес: 1063 Hu Bei Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518001	0101000020E6100000EA211ADD41885C40F19F6EA0C08B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
9d3a0f37-5e38-4daa-b84e-cd701d5e69d1	Shuiwei 1368	Establishment, point of interest	Рейтинг Google: 4.4 (22 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 1 东南方向100米	0101000020E6100000B936548CF3835C40309E4143FF843640	f	812714b9-873b-41b9-b849-acb601551000	\N
a73e8646-28e1-4602-9cfb-b8f7d1bd5cd0	OLE Supermarket (Holiday Plaza)	Establishment, food	Рейтинг Google: 5 (1 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, 益田假日广场Floor B2 邮政编码: 518058	0101000020E6100000DE74CB0E717E5C407028D76F81893640	f	812714b9-873b-41b9-b849-acb601551000	\N
3573a090-ff5d-4096-9e2b-9fb83086f713	KK One South Zone North Gate	Establishment, point of interest	Рейтинг Google: 4.3 (35 отзывов). Адрес: 9289 Bin He Da Dao, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518042	0101000020E610000019FF3EE3C2815C40825660C8EA863640	f	812714b9-873b-41b9-b849-acb601551000	\N
24587699-ff9c-4bed-8bd2-2f6217891859	OpenMind Co-Working Space Shenzhen	Establishment, point of interest	Рейтинг Google: 5 (1 отзывов). Адрес: NO.113, Village 1 莲花山庄, 布吉镇龙岗区深圳市 Китай, 518024	0101000020E61000000664AF77FF865C4016AAF64432993640	f	812714b9-873b-41b9-b849-acb601551000	\N
f4787139-ac46-476c-b90b-5118268a49fc	OpenMind Shenzhen	Establishment, point of interest	Рейтинг Google: Нет оценки (0 отзывов). Адрес: NO.113, Village 1, 莲花山庄布吉镇龙岗区深圳市 Китай, 518102	0101000020E6100000ED026F92B0795C40B37BF2B0509D3640	f	812714b9-873b-41b9-b849-acb601551000	\N
646270db-2876-433d-8ad1-022c7f32d09d	柴火创客空间	Establishment, point of interest	Рейтинг Google: 5 (1 отзывов). Адрес: Wen Chang Jie, 华侨城 Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518074	0101000020E61000002A430BBF8A7F5C4099D30A783E8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
23cc743c-7b22-4da6-8902-07bb729504b3	WeWork	Establishment, point of interest	Рейтинг Google: Нет оценки (0 отзывов). Адрес: GW5R+J8P, Nanshan, Shenzhen, Guangdong Province, Китай, 518065	0101000020E6100000E4CE96BD367C5C40881EE7EC53823640	f	812714b9-873b-41b9-b849-acb601551000	\N
cf223e96-0020-43fc-9ca8-b6e051ab830f	TCL Building Parking Lot	Establishment, point of interest	Рейтинг Google: 3.7 (11 отзывов). Адрес: 6 Gao Xin Nan Yi Dao, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518063	0101000020E6100000554FE61FFD7C5C407BE1293F048A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
4b10f62c-b780-4df8-8aa1-c929e416b42e	Shum Yip Upperhills Tower 1	Establishment, point of interest	Рейтинг Google: 4.7 (11 отзывов). Адрес: 5001 Huang Gang Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518033	0101000020E610000052CAB5B28E845C400C1DE0EE518E3640	f	812714b9-873b-41b9-b849-acb601551000	\N
ab080783-d423-4dc6-bfc6-fa92ddbbf105	Kerry Plaza 2	Establishment, point of interest	Рейтинг Google: 3.7 (3 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 福田ＣＢＤ中心四路1号 邮政编码: 518046	0101000020E6100000C539EAE8B8835C4099B8551003893640	f	812714b9-873b-41b9-b849-acb601551000	\N
6ec3ef39-a55e-49b0-87c8-9477fd5ba48c	The Executive Centre （Shenzhen） Limited	Establishment, point of interest	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, 中心城中心四路1号-1号嘉里建设广场第3座13层 邮政编码: 518046	0101000020E61000001DAF40F4A4835C4073F56393FC883640	f	812714b9-873b-41b9-b849-acb601551000	\N
d060774a-b274-41e1-a251-93323cc048ed	КАМЕРА ХРАНЕНИЯ БАГАЖА	Establishment, point of interest	Рейтинг Google: 4.2 (54 отзывов). Адрес: Вокзальна площа, 1, Київ, Украина, 02000	0101000020E6100000A4FD0FB0567D3E40F6F873C064384940	f	812714b9-873b-41b9-b849-acb601551000	\N
5d848403-2ba2-4e5b-8ec2-672c814070e6	Шэньчжэнь Баоань	Airport, establishment	Рейтинг Google: 4.2 (2596 отзывов). Адрес: JRP7+PRQ, Baoan, Shenzhen, Guangdong Province, Китай	0101000020E61000000648348122745C40562DE92807A33640	f	812714b9-873b-41b9-b849-acb601551000	\N
02ae51d8-debd-4fab-91c5-d4117eefcb85	深圳宝安国际机场A航站楼	Airport, establishment	Рейтинг Google: 4 (6 отзывов). Адрес: JRX9+646, Baoan, Shenzhen, Guangdong Province, Китай, 518128	0101000020E6100000AAD4EC8156745C40785E2A36E6A53640	f	812714b9-873b-41b9-b849-acb601551000	\N
6f84996a-39c4-431e-990f-f4cee64a8ad8	Shenzhen North Railway Station	Establishment, point of interest	Рейтинг Google: 4.1 (138 отзывов). Адрес: Baoan, Shenzhen, Китай, 518131	0101000020E6100000321D3A3DEF815C40C8B3CBB73E9C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
c273448e-e5b4-4f02-9e65-651c863ad9cd	Crowne Plaza Shenzhen Nanshan	Establishment, lodging	Рейтинг Google: 4.4 (42 отзывов). Адрес: No 9819 Shenzhen Boulevard, 南山区深圳市广东省 Китай, 518054	0101000020E610000058569A94827C5C40787B1002F2893640	f	812714b9-873b-41b9-b849-acb601551000	\N
9d6dbd3e-96fa-4369-a49b-ad7ae6c70f0d	InterContinental Shenzhen	Establishment, lodging	Рейтинг Google: 4.4 (228 отзывов). Адрес: Nanshan, Шэньчжэнь, Китай, 518053	0101000020E61000007E3B8908FF7E5C4096EA025E66883640	f	812714b9-873b-41b9-b849-acb601551000	\N
5ad07204-818c-4138-b2af-a93eb1c5585e	Courtyard by Marriott Shenzhen Bao'an	Establishment, lodging	Рейтинг Google: 4.5 (154 отзывов). Адрес: No. 46 Dongfang Rd Songgang, 宝安区深圳市广东省 Китай, 518034	0101000020E610000098FA795391765C403E5B07077BC33640	f	812714b9-873b-41b9-b849-acb601551000	\N
c51935f6-4331-43f8-83a6-2c8cc956ecd4	Four Points by Sheraton Shenzhen	Establishment, lodging	Рейтинг Google: 4 (359 отзывов). Адрес: 5 Guihua Road, 福田区深圳市广东省 Китай, 518038	0101000020E6100000689604A8A9835C4085D21742CE833640	f	812714b9-873b-41b9-b849-acb601551000	\N
429006c3-485d-4546-9eaa-a95d11a2a681	Crowne Plaza Hotel&suites Landmark Shenzhen	Establishment, lodging	Рейтинг Google: 4.3 (218 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 南湖路3018号 邮政编码: 518001	0101000020E6100000ADC3D155BA875C408BA9F413CE8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
32974c16-d058-4946-b8ee-85580ded60fa	IMAX Theater	Establishment, movie theater	Рейтинг Google: 4.6 (5 отзывов). Адрес: GXFR+2W5, Futian District, Shenzhen, Guangdong Province, Китай, 518053	0101000020E610000082035ABA827F5C40439259BDC3853640	f	812714b9-873b-41b9-b849-acb601551000	\N
0ba7cbad-ce09-466a-884b-d5defc49ebf5	Oriental Palm Spring International Club	Establishment, point of interest	Рейтинг Google: 3.7 (23 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Fu Tian Qu, Fu Qiang Lu, 2002号-2	0101000020E610000022C5008926845C40CEFA9463B2843640	f	812714b9-873b-41b9-b849-acb601551000	\N
9300fabf-a830-4d14-a32e-ee6e9613d03e	QUEEN'S SPA	Doctor, establishment	Рейтинг Google: 3.6 (20 отзывов). Адрес: G4RG+694, Chun Feng Lu, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай	0101000020E6100000BDF039660F885C40DB3928BC5F8A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
56ce1e41-11a8-4aca-abb0-49706df1bd25	皇室假期美食水疗会	Establishment, point of interest	Рейтинг Google: 3.5 (63 отзывов). Адрес: 39 Xiang Xi Lu, Man Kam To, Luo Hu Qu, Shen Zhen Shi, Guang Dong Sheng, Китай	0101000020E61000005DA3E5400F885C40118DEE20768A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
205e9b75-e64f-40d5-81e8-c2008e993462	Sentosa International Spa Club	Establishment, gym	Рейтинг Google: 2 (3 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Luo Hu Qu, 沿河路 邮政编码: 518001	0101000020E6100000C74CA25E70885C4061133E004E8C3640	f	812714b9-873b-41b9-b849-acb601551000	\N
204d69b3-a5ac-4ef5-bcaf-03f154166fe6	Shenzhen Ocean World	Aquarium, establishment	Рейтинг Google: 3.8 (56 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Yan Tian Qu, 盐葵路J83H+38X 邮政编码: 518083	0101000020E61000008733BF9A03955C40CD599F724C9A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
c80cc6d3-9112-442e-9396-d13534952057	Safari Park Shenzhen Aquarium	Aquarium, establishment	Рейтинг Google: 3.5 (2 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, 西丽湖路 邮政编码: 518071	0101000020E61000004A27124C357E5C4027BF45274B993640	f	812714b9-873b-41b9-b849-acb601551000	\N
081356a1-cb1e-4dac-81d0-967b035bdd18	Shenzhen Wild Animal Zoo （West Gate）	Establishment, point of interest	Рейтинг Google: 4.1 (33 отзывов). Адрес: HXV8+M2G, Li Shui Lu, Nan Shan Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518071	0101000020E61000002579AEEFC37D5C4015C616821C983640	f	812714b9-873b-41b9-b849-acb601551000	\N
70155cd4-a495-4881-ab96-f8cf19ab4a04	Shenzhen Sea World Sharks Hall	Aquarium, establishment	Рейтинг Google: 5 (3 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Yan Tian Qu, S30惠深沿海高速入口J83H+V62 邮政编码: 518083	0101000020E61000009697FC4FFE945C401CD2A8C0C99A3640	f	812714b9-873b-41b9-b849-acb601551000	\N
b9416032-8adc-40ea-9592-ebed02bf9230	Dream Aquarium	Amusement park, establishment	Рейтинг Google: 3.5 (36 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Nan Shan Qu, Bai Shi Lu, 白石路东8号欢乐海岸购物中心2层西侧 邮政编码: 518053	0101000020E61000001233FB3C467F5C40378AAC3594863640	f	812714b9-873b-41b9-b849-acb601551000	\N
cefc8ad3-eabc-4cfc-b7c3-d34892b92e59	Shenzhen Children's Paradise	Amusement park, establishment	Рейтинг Google: 4 (58 отзывов). Адрес: G2V7+9VC, Nong Lin Lu, Fu Tian Qu, Shen Zhen Shi, Guang Dong Sheng, Китай, 518043	0101000020E6100000446E861BF0805C40D388997D1E8B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
ff2f3ac5-2a84-4055-a198-7a34fc25d2f7	PLAYA MAYA WATER PARK-HAPPY VALLEY	Amusement park, establishment	Рейтинг Google: 5 (1 отзывов). Адрес: Китай, 广东省深圳市南山区华侨城GXVF+WH7 邮政编码: 518072	0101000020E61000006F1E98ED547E5C405E10919A768B3640	f	812714b9-873b-41b9-b849-acb601551000	\N
a9690b69-c57f-4040-9c16-4726b8c7da7b	MeLAND儿童成长乐园	Establishment, point of interest	Рейтинг Google: 4.5 (16 отзывов). Адрес: J2G9+VQR, Ren Min Lu, 宝安区 Shen Zhen Shi, Guang Dong Sheng, Китай, 518131	0101000020E61000000A4AD1CA3D815C4091C140C692A03640	f	812714b9-873b-41b9-b849-acb601551000	\N
96ad6b73-eda7-4d1d-875c-8b3ff588b617	Explore Paradise	Establishment, point of interest	Рейтинг Google: Нет оценки (0 отзывов). Адрес: Китай, Guang Dong Sheng, Shen Zhen Shi, Yan Tian Qu, 2039, 正东方向70米	0101000020E61000006891ED7C3F8F5C40679B1BD3138E3640	f	812714b9-873b-41b9-b849-acb601551000	\N
\.


--
-- Data for Name: rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rules (id, content, created_at, updated_at) FROM stdin;
6d07f900-290c-480b-8830-4b3815185e66	VPN необходим для доступа к Google, Instagram, WhatsApp — установите до въезда	2026-03-20 22:40:19.952777	2026-03-20 22:40:19.952777
933121d5-f487-40ae-b1a5-7ed29b87aef5	Основные способы оплаты — WeChat Pay и Alipay, настройте до поездки	2026-03-20 22:40:19.952777	2026-03-20 22:40:19.952777
24024f55-150f-472f-9374-fcd20af1ebe3	Чаевые не приняты в Китае и могут обидеть персонал	2026-03-20 22:40:19.952777	2026-03-20 22:40:19.952777
eefeb451-c2b6-4ded-ba51-8f5ca736c933	Фотографировать военные объекты, полицейских и пограничные зоны запрещено	2026-03-20 22:40:19.952777	2026-03-20 22:40:19.952777
241710c5-e2c1-4c50-94e4-ed55329571ff	Уважайте старших — пропускайте вперёд в очереди и транспорте	2026-03-20 22:40:19.952777	2026-03-20 22:40:19.952777
b08921f6-e410-46e6-ba4d-9b69ae68d8a1	Метро работает до 23:00 — планируйте возвращение заранее	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
aa860e95-fc35-4797-bafc-9b1d6aa9bee6	На оптовых рынках торгуйтесь — цены для туристов завышены в 2–3 раза	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
f5f021b1-eb78-4a57-8a01-e51a8318ef02	Летом (июнь–сентябрь) очень жарко и влажно — носите лёгкую одежду и воду	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
655de729-10bb-4cff-b3c3-d4ba4c4a6f45	До Терракотовой армии только организованный транспорт — не садитесь к частникам у вокзала	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
6412be1d-03ca-4a4d-943f-8cf9d77d2ceb	В Мусульманском квартале закрытая одежда обязательна при входе в мечеть	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
2bd923f3-8e25-42a8-b668-7ce82113f8d3	Городская стена — движение на велосипеде только против часовой стрелки	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
e8eab6eb-70c0-4950-9215-c26c72ffc9b5	Удобная обувь обязательна — тропы крутые и каменистые	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
46b5b542-8c1c-46c2-bdbd-5eff5e8df97f	Проверяйте прогноз погоды — в туман видимость нулевая	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
a56041f9-de39-4be4-8961-6c10a6828462	Выделите минимум 3–4 дня — за один день парк не осмотреть	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
d0cfb217-7014-49fa-8f77-d9b7a771e1cf	Купание в реке Туцзян официально запрещено	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
39a097d4-398d-4914-bae5-1eef229c10fb	Деревянные мостки скользкие в дождь — осторожно	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
8fb42674-e130-4b18-97d5-c2cc00bbc6cf	Чаевые не приняты — не оставляйте их в ресторанах	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
1896319d-6be5-4a01-a27a-8ff4b113346b	Местная кухня очень острая — предупреждайте официантов об ограничениях	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
473436c0-8d81-4f46-a1f8-c5a4375c4626	До Гуанчжоу 30 минут на метро — удобно совмещать посещения	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
33112d57-4418-4d16-89f5-6f8dcee7c4de	Аутлеты работают ежедневно 10:00–22:00	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
5fa990d0-0f0a-436d-9549-50be62fd0d50	На границе с Гонконгом очереди — приходите рано утром	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
132d4917-4332-4770-91a8-e5ef0f394034	Для въезда в Гонконг нужна отдельная виза для большинства стран	2026-03-20 22:40:20.054744	2026-03-20 22:40:20.054744
a60a3d8f-6015-4b52-920d-c60061bb6d45	Торг уместен, но вежливо — агрессивный торг воспринимается негативно	2026-03-20 22:40:20.160699	2026-03-20 22:40:20.160699
55797ce5-907b-447b-ae72-e26ca9d1e66a	Примерочные могут быть платными — уточняйте заранее	2026-03-20 22:40:20.160699	2026-03-20 22:40:20.160699
c350f1e2-76ce-4e49-ad82-50c718118df2	Обязательно торгуйтесь — начальная цена завышена в 2–5 раз	2026-03-20 22:40:20.197725	2026-03-20 22:40:20.197725
ade6b0eb-4956-4f79-a8e3-23d0a29aca06	Следите за личными вещами в толпе	2026-03-20 22:40:20.197725	2026-03-20 22:40:20.197725
da331fd7-3b19-417e-aec0-652e732f48a8	Большинство продавцов работают только оптом — уточняйте минимальный заказ	2026-03-20 22:40:20.230386	2026-03-20 22:40:20.230386
f358d2d6-4451-43d8-8ef4-f632ce98591d	Фотографировать товары у некоторых продавцов запрещено	2026-03-20 22:40:20.230386	2026-03-20 22:40:20.230386
1b29d822-cd9d-4be5-a163-4882e7f83f53	Многие продавцы понимают русский язык — можно общаться	2026-03-20 22:40:20.263696	2026-03-20 22:40:20.263696
d1ce3c2d-1d0b-4dc7-b4dd-1c132531ce5b	Цены на входе завышены — всегда торгуйтесь	2026-03-20 22:40:20.263696	2026-03-20 22:40:20.263696
4fa359d1-2d0a-4533-96d8-53d99cafb2f9	Вспышка при фотосъёмке запрещена в музейных залах	2026-03-20 22:40:20.290046	2026-03-20 22:40:20.290046
e3e145c8-13c4-4693-bbc7-e5d5da61117a	Еда и напитки запрещены на территории раскопок	2026-03-20 22:40:20.290046	2026-03-20 22:40:20.290046
fd8b26fa-f6e4-4950-96e8-c111bcda3d21	В мечеть вход только в скромной одежде — плечи и колени закрыты	2026-03-20 22:40:20.321201	2026-03-20 22:40:20.321201
cebb7f0b-b8a2-4039-beef-ff327c8c7fc6	Фотографировать молящихся запрещено	2026-03-20 22:40:20.321201	2026-03-20 22:40:20.321201
b3f9db8e-75cf-40bc-9e9a-f4db358bffd4	Свинина в квартале не подаётся — это халяльная зона	2026-03-20 22:40:20.321201	2026-03-20 22:40:20.321201
b14ef6e0-d09a-4e26-a775-b2b261b8c2a3	Велосипеды движутся только против часовой стрелки	2026-03-20 22:40:20.355475	2026-03-20 22:40:20.355475
d906b16f-2e8f-41b7-9658-ba51d9598a7f	Скромная одежда при входе — плечи и колени закрыты	2026-03-20 22:40:20.377269	2026-03-20 22:40:20.377269
e5f7c653-d725-4ead-8cb7-d63bc7890197	Говорите тихо на территории буддийского комплекса	2026-03-20 22:40:20.377269	2026-03-20 22:40:20.377269
a1595758-677b-4293-a900-f11c63f17ef4	Удобная обувь обязательна — тропы каменистые и крутые	2026-03-20 22:40:20.388475	2026-03-20 22:40:20.388475
d838f7de-25fe-4594-886c-02149c03d530	Не выходить за ограждения и на закрытые тропы	2026-03-20 22:40:20.388475	2026-03-20 22:40:20.388475
c393dc5c-0a25-470a-89f7-4c974a1258e7	Еду выносить из парка нельзя — штраф	2026-03-20 22:40:20.388475	2026-03-20 22:40:20.388475
2b0d23b0-c26c-4028-9858-83fa6787b696	Купание в реке Туцзян запрещено — официальный запрет властей	2026-03-20 22:40:20.421201	2026-03-20 22:40:20.421201
e1cd48e4-2069-4390-9bb2-58c1cc3e6147	В дождь деревянные мостки скользкие — осторожно	2026-03-20 22:40:20.421201	2026-03-20 22:40:20.421201
a755387e-def1-4063-8618-07cc95393fbd	Блюдо очень острое — предупредите официанта если не переносите острое	2026-03-20 22:40:20.442316	2026-03-20 22:40:20.442316
0e3d70b9-4e25-41e3-9ecb-6f76b817c5d2	Чаевые не приняты в Китае — не оставляйте их	2026-03-20 22:40:20.442316	2026-03-20 22:40:20.442316
6d0714cb-2e44-4985-a515-7c73b43c42e8	Скидочные купоны доступны в приложении WeChat	2026-03-20 22:40:20.470841	2026-03-20 22:40:20.470841
10fd6ea7-bdb9-41d7-8350-2cfdefe40daa	Парковка платная — 10 юаней/час	2026-03-20 22:40:20.470841	2026-03-20 22:40:20.470841
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: trip_pois; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip_pois (trip_id, poi_id, sequence_order, planned_start_time, poi_status, is_selected, day_number) FROM stdin;
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	6bd83839-f62d-4997-b88d-b2265cb3002c	\N	\N	additional	f	1
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	f008ec05-8aa4-4112-9f0a-45be906ba598	\N	\N	additional	f	1
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	a9b972da-2c4a-4b11-a8c6-a0cb1e282f4e	\N	\N	additional	f	1
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	ff6f4433-c73a-46c2-9371-3ba6c6189b76	\N	\N	additional	f	1
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	6d326d4b-1847-4166-9b01-464c051b0d5a	\N	\N	main	t	2
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	d3a241d2-439c-40a0-bf32-a91393ad8f0a	\N	\N	main	t	2
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	081742e7-529a-4eff-a149-232017b17997	\N	\N	main	t	2
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	1f746411-6e76-40ba-9a9a-5924e66bdce6	\N	\N	main	t	2
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	17074173-ea05-4981-8003-cec196ef0e04	\N	\N	additional	f	2
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	35ad1bbc-fbf0-41d4-b6cb-ce0a2b8d0ab5	\N	\N	additional	f	2
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	120373c8-1243-432e-8791-d808e44835ad	\N	\N	additional	f	2
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	a676f97c-9dea-4ce3-a036-ccc09344e5dc	\N	\N	additional	f	2
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	e0d98b06-2da5-4a1c-8856-39620d11bcd9	\N	\N	main	t	3
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	e1a50791-5448-47a0-900e-ae109f4b0119	\N	\N	main	t	3
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	2e1e501a-8bf0-48e3-b001-a594fb0f1590	\N	\N	main	t	3
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	f5b0a3a0-6bd2-4721-bec0-55d6625f3830	\N	\N	additional	f	3
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	276b181d-bc58-4b39-b244-4aa4119df773	\N	\N	additional	f	3
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	16cccd61-0216-49b8-bc4b-e8d8e78f6a49	\N	\N	additional	f	3
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	6dc6f93a-358e-4f25-9b73-ef0acb32221c	\N	\N	additional	f	3
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	7a9ccaaf-3b96-4b7d-a485-a426c4b6a279	\N	\N	main	t	4
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	7303694a-eee4-455d-8989-31e71ca9e762	\N	\N	main	t	4
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	d14c666c-9295-494b-bf00-9e86e078674e	\N	\N	main	t	4
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	10d1fd66-b171-45cf-8f84-31205ec96b85	\N	\N	main	t	4
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	c387aba5-a85e-4cfc-822b-4596f1f61ea0	\N	\N	additional	f	4
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	d98903fe-3d9c-4d35-a6ad-d2b160711eb4	\N	\N	additional	f	4
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	6b10c4ab-1af5-43c3-ab97-ca31d28fdb3b	\N	\N	additional	f	4
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	c95cf007-c592-43f4-92d8-74adb323ffc4	\N	\N	additional	f	4
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	bb2ed172-fffd-42f3-8cc4-d873f033811e	\N	\N	main	t	5
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	e4c8d8c7-17a3-4972-8166-d24e50925aa6	\N	\N	main	t	5
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	70155cd4-a495-4881-ab96-f8cf19ab4a04	\N	\N	main	t	5
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	9f5a5022-c94a-47de-9818-71ba2743cfb1	\N	\N	main	t	5
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	b9416032-8adc-40ea-9592-ebed02bf9230	\N	\N	additional	f	5
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	7169319a-14ea-4c8a-916c-f336e86456a1	\N	\N	additional	f	5
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	29fc4e82-29a4-4809-a636-5ffcaf9466b3	\N	\N	additional	f	5
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	c6b8b786-d1d9-4a83-b696-8cd3cb32e731	\N	\N	additional	f	5
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	ab42e063-f333-4d48-8304-9e2d843569b1	\N	\N	main	t	6
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	07383845-ccb6-4715-8a44-03b864ba780a	\N	\N	main	t	6
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	56ce1e41-11a8-4aca-abb0-49706df1bd25	\N	\N	main	t	6
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	3118db1c-69e5-465e-9492-71b8647d84d9	\N	\N	main	t	6
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	fa7e63c8-175f-498f-8d74-fd12dda31238	\N	\N	additional	f	6
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	ff61fb13-00fe-4d6b-b336-71f6092d0e48	\N	\N	additional	f	6
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	9300fabf-a830-4d14-a32e-ee6e9613d03e	\N	\N	additional	f	6
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	42dd7b3c-e2a5-41d3-ba9d-2c00de1017e1	\N	\N	additional	f	6
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	86bba304-5ef7-4fba-abc2-097dd49abfff	3	\N	main	t	1
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	b8c7de24-1617-48d7-9b46-ee3d71fd56e6	4	\N	main	t	1
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	e4e494b5-3838-4a41-ad04-ff095a6133f5	2	\N	main	t	1
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	80a51eb1-324e-4053-a67d-4ae36258b925	\N	\N	additional	f	1
\.


--
-- Data for Name: trips; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trips (id, user_id, country_id, city_id, purpose, budget, group_size, other_information, start_date, end_date, created_at) FROM stdin;
e6e49ab8-452d-4f26-a9a1-4c076b5e543a	b4984b53-6f11-44a0-9dd1-cd8b6d1657bf	30891716-033e-41ad-9893-631af79ad11a	812714b9-873b-41b9-b849-acb601551000	leisure	medium	1	{"Хочется отдохнуть и понять культуру страны и города"}	2026-05-05	2026-05-10	2026-05-05 14:10:14.55881
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, hashed_password, created_at, updated_at) FROM stdin;
b4984b53-6f11-44a0-9dd1-cd8b6d1657bf	user@example.com	$2b$12$rf2RcHH/N0zX8B3YnvZ/mO818bS8gyyyP1fDzL2CJj985n6SyqeEi	2026-05-05 14:08:44.501134	2026-05-05 14:08:44.501134
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: cities cities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_pkey PRIMARY KEY (id);


--
-- Name: city_rules city_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.city_rules
    ADD CONSTRAINT city_rules_pkey PRIMARY KEY (city_id, rule_id);


--
-- Name: countries countries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.countries
    ADD CONSTRAINT countries_pkey PRIMARY KEY (id);


--
-- Name: country_rules country_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.country_rules
    ADD CONSTRAINT country_rules_pkey PRIMARY KEY (country_id, rule_id);


--
-- Name: cities idx_cities_country_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT idx_cities_country_name UNIQUE (country_id, name);


--
-- Name: poi_rules poi_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.poi_rules
    ADD CONSTRAINT poi_rules_pkey PRIMARY KEY (poi_id, rule_id);


--
-- Name: pois pois_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pois
    ADD CONSTRAINT pois_pkey PRIMARY KEY (id);


--
-- Name: rules rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rules
    ADD CONSTRAINT rules_pkey PRIMARY KEY (id);


--
-- Name: trip_pois trip_pois_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip_pois
    ADD CONSTRAINT trip_pois_pkey PRIMARY KEY (trip_id, poi_id);


--
-- Name: trips trips_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trips
    ADD CONSTRAINT trips_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_pois_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pois_geom ON public.pois USING gist (geom);


--
-- Name: ix_countries_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_countries_name ON public.countries USING btree (name);


--
-- Name: ix_pois_city_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pois_city_id ON public.pois USING btree (city_id);


--
-- Name: ix_pois_google_place_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_pois_google_place_id ON public.pois USING btree (google_place_id);


--
-- Name: ix_trips_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_trips_user_id ON public.trips USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: cities cities_country_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id) ON DELETE CASCADE;


--
-- Name: city_rules city_rules_city_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.city_rules
    ADD CONSTRAINT city_rules_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities(id) ON DELETE CASCADE;


--
-- Name: city_rules city_rules_rule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.city_rules
    ADD CONSTRAINT city_rules_rule_id_fkey FOREIGN KEY (rule_id) REFERENCES public.rules(id) ON DELETE CASCADE;


--
-- Name: country_rules country_rules_country_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.country_rules
    ADD CONSTRAINT country_rules_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id) ON DELETE CASCADE;


--
-- Name: country_rules country_rules_rule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.country_rules
    ADD CONSTRAINT country_rules_rule_id_fkey FOREIGN KEY (rule_id) REFERENCES public.rules(id) ON DELETE CASCADE;


--
-- Name: poi_rules poi_rules_poi_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.poi_rules
    ADD CONSTRAINT poi_rules_poi_id_fkey FOREIGN KEY (poi_id) REFERENCES public.pois(id) ON DELETE CASCADE;


--
-- Name: poi_rules poi_rules_rule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.poi_rules
    ADD CONSTRAINT poi_rules_rule_id_fkey FOREIGN KEY (rule_id) REFERENCES public.rules(id) ON DELETE CASCADE;


--
-- Name: pois pois_city_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pois
    ADD CONSTRAINT pois_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities(id) ON DELETE CASCADE;


--
-- Name: trip_pois trip_pois_poi_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip_pois
    ADD CONSTRAINT trip_pois_poi_id_fkey FOREIGN KEY (poi_id) REFERENCES public.pois(id) ON DELETE CASCADE;


--
-- Name: trip_pois trip_pois_trip_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip_pois
    ADD CONSTRAINT trip_pois_trip_id_fkey FOREIGN KEY (trip_id) REFERENCES public.trips(id) ON DELETE CASCADE;


--
-- Name: trips trips_city_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trips
    ADD CONSTRAINT trips_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities(id) ON DELETE RESTRICT;


--
-- Name: trips trips_country_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trips
    ADD CONSTRAINT trips_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id) ON DELETE RESTRICT;


--
-- Name: trips trips_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trips
    ADD CONSTRAINT trips_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict VjX3rhDTl1yrws8ATbuttKqDsrybWmDEcjKfZDWZwrZ9wsOIGk2Bf0U3hR40KHC

