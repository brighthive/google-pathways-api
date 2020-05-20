import json
import os


class ConfigurationError(Exception):
    pass

class Configuration(object):
    def find_json_config_file(self):
        """Find JSON configuration file.

        Locate the JSON configuration relative to the application path.
        Returns:
            str: Configuration file.
        Raises:
            ConfigurationError: If the configuration file cannot be found.
        """

        absolute_path = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(absolute_path, "config.json")

        if os.path.exists(config_file) and os.path.isfile(config_file):
            return config_file
        else:
            raise ConfigurationError(
                "Cannot find configuration file in path {}.".format(absolute_path)
            )

    def load_json_config(self, config_file: str):
        """Load application configuration from JSON file.

        Args:
            config_file (str): The path and name of the configuration file to load.
        Returns:
            dict: Configuration object.
        Raises:
            ConfigurationError: If the configuration file doesn't exist or
                cannot be loaded because of a syntax error.
        """

        if not os.path.exists(config_file) or not os.path.isfile(config_file):
            raise ConfigurationError(
                "Error loading configuration file {}.".format(config_file)
            )

        try:
            with open(config_file, "r") as f:
                data = json.load(f)
            return data
        except Exception:
            raise ConfigurationError(
                "Failed to load configuration file {}. Please check the configuration file.".format(
                    config_file
                )
            )

    def from_json(self, environment="local"):
        """Load application configuration from JSON object based on the
        configuration type.

        Args:
            environment (str): The environment to load.
        Raises:
            ConfigurationError: If the JSON configuration cannot be loaded.
        """

        config_file = self.find_json_config_file()
        data = self.load_json_config(config_file)

        if environment in data.keys():
            fields = data[environment]
            try:
                self.BASE_URL = fields["base_url"]

                self.PSQL_USER = fields["psql_user"]
                self.PSQL_PASSWORD = fields["psql_password"]
                self.PSQL_HOSTNAME = fields["psql_hostname"]
                self.PSQL_PORT = fields["psql_port"]
                self.PSQL_DATABASE = fields["psql_database"]

                self.environment = environment
                self.debug = True
                self.testing = True
            except Exception:
                raise ConfigurationError(
                    "Invalid key in JSON configuration. Please check the configuration."
                )
            else:
                self.SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}:{}/{}".format(
                    self.PSQL_USER,
                    self.PSQL_PASSWORD,
                    self.PSQL_HOSTNAME,
                    self.PSQL_PORT,
                    self.PSQL_DATABASE,
                )

                self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        else:
            raise ConfigurationError(
                "Cannot find environment '{}' in JSON configuration."
            )


class TestingConfiguration(Configuration):
    """Configuration class for local development."""

    def __init__(self):
        # self.from_json("testing")
        self.debug = True
        self.testing = True

        self.CONTAINER_NAME = "test_postgres_service"
        self.IMAGE_NAME = "postgres"
        self.IMAGE_VERSION = "12"

        self.BASE_URL = "http://0.0.0.0:8000"
        self.PSQL_USER = "dt_admin_test"
        self.PSQL_PASSWORD = "passw0rd"
        self.PSQL_HOSTNAME = "localhost"
        self.PSQL_PORT = "10031"
        self.PSQL_DATABASE = "pathways_test"

        self.SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}:{}/{}".format(
                    self.PSQL_USER,
                    self.PSQL_PASSWORD,
                    self.PSQL_HOSTNAME,
                    self.PSQL_PORT,
                    self.PSQL_DATABASE,
                )
                
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        
class JenkinsConfiguration(Configuration):
    """Configuration class for local development."""

    def __init__(self):
        # self.from_json("testing")
        self.debug = True
        self.testing = True

        self.CONTAINER_NAME = "test_postgres_service"
        self.IMAGE_NAME = "postgres"
        self.IMAGE_VERSION = "12"

        self.BASE_URL = "http://0.0.0.0:8000"
        self.PSQL_USER = "dt_admin_test"
        self.PSQL_PASSWORD = "passw0rd"
        self.PSQL_HOSTNAME = os.getenv('DB_PORT_5432_TCP_ADDR', '0.0.0.0')
        self.PSQL_PORT = os.getenv('DB_PORT_5432_TCP_PORT', 5432)
        self.PSQL_DATABASE = "pathways_test"

        self.SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}:{}/{}".format(
            self.PSQL_USER,
            self.PSQL_PASSWORD,
            self.PSQL_HOSTNAME,
            self.PSQL_PORT,
            self.PSQL_DATABASE,
        )
                
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalConfiguration(Configuration):
    """Configuration class for local development."""

    def __init__(self):
        # self.from_json("local")
        self.debug = True
        self.testing = True

        self.BASE_URL = "http://0.0.0.0:8000"
        self.PSQL_USER = "brighthive_admin"
        self.PSQL_PASSWORD = "passw0rd"
        self.PSQL_HOSTNAME = "postgres_service"
        self.PSQL_PORT = "5432"
        self.PSQL_DATABASE = "pathways"

        self.SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}:{}/{}".format(
                    self.PSQL_USER,
                    self.PSQL_PASSWORD,
                    self.PSQL_HOSTNAME,
                    self.PSQL_PORT,
                    self.PSQL_DATABASE,
                )
                
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfiguration(Configuration):
    """Configuratuon class for production deployment."""

    def __init__(self):
        # self.from_json("production")
        self.debug = False
        self.testing = False

        self.BASE_URL = os.getenv("BASE_URL", "")
        self.PSQL_USER = os.getenv("PSQL_USER", "")
        self.PSQL_PASSWORD = os.getenv("PSQL_PASSWORD", "")
        self.PSQL_HOSTNAME = os.getenv("PSQL_HOSTNAME", "")
        self.PSQL_PORT = os.getenv("PSQL_PORT", "")
        self.PSQL_DATABASE = os.getenv("PSQL_DATABASE", "")

        self.SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}:{}/{}".format(
            self.PSQL_USER,
            self.PSQL_PASSWORD,
            self.PSQL_HOSTNAME,
            self.PSQL_PORT,
            self.PSQL_DATABASE,
        )
                
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False


class ConfigurationFactory(object):
    @staticmethod
    def get_config(config_type: str):
        if config_type.upper() == "TESTING":
            is_jenkins = bool(int(os.getenv('IS_JENKINS_TEST', '0')))
            if is_jenkins:
                return JenkinsConfiguration()
            else:
                return TestingConfiguration()
        if config_type.upper() == "LOCAL":
            return LocalConfiguration()
        if config_type.upper() == "PRODUCTION":
            return ProductionConfiguration()

    @staticmethod
    def from_env():
        """Retrieve configuration based on environment settings.

        Provides a configuration object based on the settings found in the `APP_ENV` variable. Defaults to the `local`
        environment if the variable is not set.
        Returns:
            object: Configuration object based on the configuration environment found in the `APP_ENV` environment variable.
        """
        environment = os.getenv("APP_ENV", "LOCAL")

        return ConfigurationFactory.get_config(environment)
