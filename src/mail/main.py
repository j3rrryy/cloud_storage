import uvloop

from config import load_config
from service import MailService
from services import connect_kafka_service


async def main():
    consumer = connect_kafka_service()
    service = MailService(consumer)
    await service.process_messages()
    load_config().app.logger.info("Server started")


if __name__ == "__main__":
    uvloop.run(main())
