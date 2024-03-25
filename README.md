
# Projeto Computação em Nuvem - 2023.1 
## Aluno: Marcel Pinheiro Caraciolo (mpc3@cesar.school)


# Projeto
Este projeto consiste no uso das tecnologias S3, Athena e Glue provisionadas por meio da tecnologia CDK Toolkit em Python na AWS.

## Arquitetura

- Ao provisionar o ambiente em CDK já realizamos o upload dos 2 arquivos de base de dados da empresa fictícia 5GFlix na zona **landing** em um bucket no S3.
- Temos um Job Glue provisionado para realizar as tarefas de pré-processamento dos dados (limpeza, extração de colunas, e armazenamento em formato parquet).
- Os dados processados são armazenados em parquet na zona **transformada** em um bucket no S3.
- Temos um job Crawler Glue que realiza o mapeamento e inferência das base de dados e armazena os dados em um database para consultas futuras em Athena.
- Temos um workspace no Athena com consultas em SQL mapeadas para respostas de análise das perguntas solicitadas pela gestão do 5GFlix (objetivo do exercício).


![Projeto Infra-Cloud drawio](https://github.com/marcelcaraciolo/cesar-dados-cloud/assets/275084/95b855a3-24d0-4cac-8927-b3218629f918)

## Evidências

- Ao provisionar o ambiente em CDK já realizamos o upload dos 2 arquivos de base de dados da empresa fictícia 5GFlix na zona **landing** em um bucket no S3.
![image](https://github.com/marcelcaraciolo/cesar-dados-cloud/assets/275084/7d56a0a4-02d9-4e0f-95b2-b30c54ea1930)

- Temos um Job Glue provisionado para realizar as tarefas de pré-processamento dos dados (limpeza, extração de colunas, e armazenamento em formato parquet).
![image](https://github.com/marcelcaraciolo/cesar-dados-cloud/assets/275084/f1acf0e1-a7a0-473d-9702-92a1e245acab)

[Codigo Fonte](https://github.com/marcelcaraciolo/cesar-dados-cloud/blob/main/resources/glue-scripts/transform_job.py)

- Os dados processados são armazenados em parquet na zona **transformada** em um bucket no S3.
![image](https://github.com/marcelcaraciolo/cesar-dados-cloud/assets/275084/3b85fc4c-e093-420f-a607-7085198f2f50)

- Temos um job Crawler Glue que realiza o mapeamento e inferência das base de dados e armazena os dados em um database para consultas futuras em Athena.
<img width="1164" alt="Captura de Tela 2024-03-25 às 15 21 05" src="https://github.com/marcelcaraciolo/cesar-dados-cloud/assets/275084/4855da2c-9aca-4576-a05f-900fd6730b09">

- Temos um workspace no Athena com consultas em SQL mapeadas para respostas de análise das perguntas solicitadas pela gestão do 5GFlix (objetivo do exercício).
<img width="1398" alt="Captura de Tela 2024-03-25 às 15 22 16" src="https://github.com/marcelcaraciolo/cesar-dados-cloud/assets/275084/cbcf1d10-ac6d-4dfc-83c6-073701426444">


## Evidências Consultas

### Quantos filmes estão disponíveis no dataset?

## Como executar

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
