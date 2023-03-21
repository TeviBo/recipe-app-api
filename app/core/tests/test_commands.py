"""
Test custom Django management commands.
"""

from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase
from psycopg2 import OperationalError as Psycopg2Error


@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for db if db ready."""
        # Debemos mockear el comportamiento agregando el decorator patch
        # Mediante esta linea establecemos que lo que queremos que retorne el check es simplemente un valor, en este caso True.
        patched_check.return_value = True

        call_command("wait_for_db")
        # Se asegura que el objeto mockeado, se llame con los parametros enviados.
        patched_check.assert_called_once_with(databases=["default"])

    # Los argumentos se aplican desde dentro hacia afuera, por lo cual hay que respetar la ubicacion en la definicion del metodo. En este caso el sleep se llama dentro de la clase por lo cual se importa primero
    @patch("time.sleep")
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for db when getting OperationalError."""

        # Nos permite pasar varios items diferentes que pueden ser manejados de distintas maneras dependiendo el tipo de error

        # Las primeras 2 veces elevamos Psycopg2Error y la segunda vez, elevamos 3 veces OperationalError
        # Esto se hace porque tal vez las primeras 2 veces el problema fue que no se levanto aun la bd por lo cual, la bd, arroja el Psycopg2Error y la segunda vez es porque  tal vez se levanto correctamente la bd pero no se levanto la bd de testing, en este caso, Django arroja el OperationalError.
        # Al final, la ultima vez que la llamemos, en este caso a la sexta, el metodo devolvera True ya que todo se ejecuto correctamente

        patched_check.side_effect = (
            [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]
        )

        call_command("wait_for_db")

        # Con esto nos aseguramos que solo se llama las veces que establecimos aqui en el test
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=["default"])
