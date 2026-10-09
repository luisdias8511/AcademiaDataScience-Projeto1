
/*
========================================================
CRIAR USUÁRIO E LOGIN
DEVE SER FEITO NO MASTER
========================================================
*/
CREATE LOGIN environment_api
WITH PASSWORD = '******';

CREATE USER environment_api
FOR LOGIN environment_api;