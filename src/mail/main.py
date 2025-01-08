import uvloop

from config import load_config
from service import MailService
from services import connect_kafka_service


async def main():
    consumer = connect_kafka_service()
    service = MailService(consumer)
    load_config().app.logger.info("Server started")
    await service.process_messages()


if __name__ == "__main__":
    uvloop.run(main())
