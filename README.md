# Drupal Converter Scripts

A collection of Drupal converter scrips written in Python.

## nodeexport2logya.py

This script processes a CSV dump created with the [node_export module](https://www.drupal.org/project/node_export).

### Prerequisites

Download and enable node_export using drush in the root directory of the Drupal site.

    drush dl uuid
    drush en uuid
    drush dl node_export
    drush en node_export
    drush en node_export_dsv

In the settings for node_export `admin/settings/node_export` enable `DSV` under `Format to use when exporting a node`. The export all nodes to a CSV file:

    drush --format=dsv ne-export > nodes.csv

For more information on how to use node_export with Drush run:

    drush help ne-export

Finally run the converter script in the root of a freshly created Logya site:

    /path/to/nodeexport2logya.py /path/to/nodes.csv /path/to/drupal.map.py