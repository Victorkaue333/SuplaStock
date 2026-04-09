@echo off
REM =====================================================
REM SCRIPT DE DEPLOY PARA WINDOWS - suplastock
REM =====================================================
REM Uso: deploy.bat [development|docker]
REM
REM Modos:
REM   development - Executa localmente com runserver
REM   docker      - Sobe containers Docker

setlocal enabledelayedexpansion

set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=development

echo ==============================================
echo   suplastock - DEPLOY %ENVIRONMENT%
echo ==============================================

cd /d "%~dp0\.."

if "%ENVIRONMENT%"=="docker" goto :docker

:local
REM =============== MODO LOCAL ===============

REM 1. Verificar arquivo .env
echo [1/7] Verificando arquivos...
if not exist "suplastock\config\.env" (
    echo AVISO: Arquivo suplastock\config\.env nao encontrado, usando valores padrao.
    echo Copie suplastock\config\.env.example para suplastock\config\.env e configure.
)

REM 2. Ativar ambiente virtual
echo [2/7] Ativando ambiente virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Criando ambiente virtual...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM 3. Instalar dependencias
echo [3/7] Instalando dependencias...
pip install -r requirements.txt -q

REM 4. Executar migracoes
echo [4/7] Executando migracoes...
cd suplastock
python manage.py migrate --noinput

REM 5. Coletar arquivos estaticos
echo [5/7] Coletando arquivos estaticos...
python manage.py collectstatic --noinput

REM 6. Verificar sistema
echo [6/7] Verificando sistema...
python manage.py check

REM 7. Iniciar servidor
echo [7/7] Iniciando servidor de desenvolvimento...
python manage.py runserver 0.0.0.0:8000
goto :end

:docker
REM =============== MODO DOCKER ===============
echo [1/4] Verificando arquivo de configuracao...
if not exist "suplastock\config\.env" (
    echo ERRO: Arquivo suplastock\config\.env nao encontrado!
    echo Copie suplastock\config\.env.example para suplastock\config\.env e configure.
    exit /b 1
)

echo [2/4] Construindo imagens Docker...
docker-compose build

echo [3/4] Iniciando containers...
docker-compose up -d

echo [4/4] Verificando status...
docker-compose ps

echo.
echo ==============================================
echo   DOCKER INICIADO COM SUCESSO!
echo ==============================================
echo.
echo Para ver logs: docker-compose logs -f web
echo Para parar: docker-compose down

:end
endlocal

