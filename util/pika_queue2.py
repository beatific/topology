'''
Created on 2016. 1. 29.

@author: P067880
'''

import json
import pika


class QueueManager(object):
    
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'topic'
    PUBLISH_INTERVAL = 1
    QUEUE = 'message'
    ROUTING_KEY = 'message'
    
    def __init__(self, host):
        
        self._connect = None
        self._url = host
        
    def connect(self):
        
        self._connect = pika.SelectConnection(pika.URLParameters(self._url),
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)
        
    def on_connection_open(self, unused_connection):
        self.add_on_connection_close_callback()
        self.open_channel()
        
    def add_on_connection_close_callback(self):
        self._connection.add_on_close_callback(self.on_connection_closed)
        
    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self._connection.add_timeout(5, self.reconnect)
            
    def reconnect(self):
        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0

        self._connection.ioloop.stop()
        self._connection = self.connect()

        self._connection.ioloop.start()
    
    def open_channel(self):
        self._connection.channel(on_open_callback=self.on_channel_open)
    
    def on_channel_open(self, channel):
        self._channel = channel
        self.add_on_channel_close_callback()
        
    def add_on_channel_close_callback(self):
        self._channel.add_on_close_callback(self.on_channel_closed)
        
    def on_channel_closed(self, channel, reply_code, reply_text):
        if not self._closing:
            self._connection.close()
            
    def get(self, exchange_name, queue_name, routing_key, exchange_type):
        self.queue_name = queue_name
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.exchange_type = exchange_type
        self.setup_exchange(exchange_name)
        self.add_on_cancel_callback()
        
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.QUEUE)
        
    def setup_exchange(self, exchange_name):
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self.exchange_type)
        
        
    def on_exchange_declareok(self, unused_frame):
        self.setup_queue(self.queue_name)
        
    def setup_queue(self, queue_name):
        self._channel.queue_declare(self.on_queue_declareok, queue_name)
        
    def on_queue_declareok(self, method_frame):
        self._channel.queue_bind(self.on_bindok, self.queue_name,
                                 self.exchange_name, self.routing_key)
        
    def on_bindok(self, unused_frame):
#         self.start_publishing()
#         self.start_consuming()
        pass

    
    def start_publishing(self):
        self.enable_delivery_confirmations()
        self.schedule_next_message()
        
    def enable_delivery_confirmations(self):
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        if confirmation_type == 'ack':
            self._acked += 1
        elif confirmation_type == 'nack':
            self._nacked += 1
        self._deliveries.remove(method_frame.method.delivery_tag)

    def schedule_next_message(self):
        if self._stopping:
            return
        self._connection.add_timeout(self.PUBLISH_INTERVAL,
                                     self.publish_message)

    def publish_message(self):
        if self._stopping:
            return

        message = {u'مفتاح': u' قيمة',
                   u'键': u'值',
                   u'キー': u'値'}
        properties = pika.BasicProperties(app_id='example-publisher',
                                          content_type='application/json',
                                          headers=message)

        self._channel.basic_publish(self.EXCHANGE, self.ROUTING_KEY,
                                    json.dumps(message, ensure_ascii=False),
                                    properties)
        self._message_number += 1
        self._deliveries.append(self._message_number)
        self.schedule_next_message()
        
    def start_consuming(self):
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.QUEUE)
        
    def add_on_cancel_callback(self):
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)   
        
    def on_consumer_cancelled(self, method_frame):
        if self._channel:
            self._channel.close()  
            
    def on_message(self, unused_channel, basic_deliver, properties, body):
        self.acknowledge_message(basic_deliver.delivery_tag)
        
    def acknowledge_message(self, delivery_tag):
        self._channel.basic_ack(delivery_tag)
        
    def stop_consuming(self):
        if self._channel:
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)
            
    def on_cancelok(self, unused_frame):
        self.close_channel()
        
    def close_channel(self):
        self._channel.close()
        
    def close_connection(self):
        self._connection.close()
        
