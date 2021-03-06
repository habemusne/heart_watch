import os
import requests
import json
from os import getenv
from os.path import join

from util.logger import logger
from util.resource import Resource


class Topic(Resource):
    def __init__(self, control_center_host, topic_name, num_partitions, replication_factor=1, long_last=False):
        self.name = topic_name
        self._num_partitions = num_partitions
        self._replication_factor = replication_factor
        self._base_url = 'http://{}:9021/2.0'.format(control_center_host)
        self._cluster_id = json.loads(requests.get(join(self._base_url, 'clusters/kafka')).text)[0]['clusterId']
        self._long_last = long_last

    @Resource.log_notify
    def create(self, force_exit=True):
        payload = {
            'name': self.name,
            'numPartitions': self._num_partitions,
            'replicationFactor': self._replication_factor,
            'configs': {
                'cleanup.policy': 'delete',
                'delete.retention.ms': getenv('KAFKA_LOG_DELETE_RETENTION_MS'),  # 1 minute
                'max.message.bytes': 1000012,
                'min.insync.replicas': '1',
                'retention.bytes': getenv('KAFKA_RENTENTION_BYTES'),
                'retention.ms': getenv('KAFKA_RETENTION_MS_LONG') if self._long_last else getenv('KAFKA_RETENTION_MS_SHORT'),
            },
        }
        response = requests.put(
            join(self._base_url, 'kafka', self._cluster_id, 'topics?validate=false'),
            json=payload,
        )
        if response.status_code >= 400:
            logger.error('Unable to create topic: {}'.format(self.name))
            logger.error(response.text)
            exit(1) if force_exit else None

    @Resource.log_notify
    def delete(self):
        raise NotImplementedError('Delete\'s REST API was not hacked.')
