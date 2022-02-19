# Trace-USDT-TRC20-transactions

Trace USDT/TRC20 transactions for any address and option to send telegram notifications for the new transaction and option to send summary of previous day through telegram bot.


## Authors

- [@Vijaya Raghavan](https://www.github.com/vij1ay)


## Deployment

To deploy this project run

```
  # create virtualenv
  # activate environment and install pip dependencies using below command
  pip install -r requirements.txt
```

Once dependency installed, The app can be run from command line using below command.
```
python main.py -app tron -config_file tron_conf.ini
```
Configuration file having all api information/ address to track/ telegram notification id/ etc.

Multiple configuration file can be created inside conf folder and it shall run as independent process.

Once started the app will run forever until stopped.
## 🚀 About Me
Architect | System Integration | Python | NodeJS | Kafka | AWS | NoSQL | RDBMS | Full Stack | Micro Services
