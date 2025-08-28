import logging
from .smart_contract import SmartContract
from .metering_event import MeteringEvent
from .batch_ready_event import BatchReadyEvent
from .metering_event_observer import MeteringEventObserver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractConsumer(MeteringEventObserver):
    def __init__(self, smart_contract: SmartContract):
        self.contract = smart_contract
        self.blocked = False

    async def handle(self, event: MeteringEvent) -> None:
        if self.blocked and isinstance(event, BatchReadyEvent):
            await self._handle_blocked_state(event)
            return

        if self.blocked:
            raise IllegalStateException("Refund the smart contract to continue using this library.")

        if isinstance(event, BatchReadyEvent):
            self._consume_from_contract(event)

    async def _handle_blocked_state(self, batch_event: BatchReadyEvent):
        await self._attempt_unblocking(batch_event.batch_sum)
        if self.blocked:
            raise IllegalStateException("Refund the smart contract to continue using this library.")

        try:
            self._consume_from_contract(batch_event)
        except Exception as e:
            logger.error("Failed to consume from contract.", exc_info=True)
            raise

    def _consume_from_contract(self, batch_event: BatchReadyEvent):
        try:
            self.contract.consume(batch_event.batch_sum)
        except Exception as e:
            self.blocked = True
            logger.error(
                "Failed to consume from contract, switching to 'blocked' state. "
                "Refund the smart contract to continue using this library.",
                exc_info=True
            )
            raise RuntimeError("Failed to consume from contract") from e

    async def _attempt_unblocking(self, required_amount: int):
        logger.debug("Attempting to unblock contract consumer...")
        try:
            available_funds = self.contract.get_client_funding()
            logger.debug(f"Available funds: {available_funds}, Required amount: {required_amount}")

            if available_funds >= required_amount:
                self.blocked = False
                logger.info(f"Contract consumer unblocked with sufficient funds: {available_funds} (required: {required_amount})")
            else:
                logger.warning(
                    f"Not enough funding available, remaining blocked. "
                    f"Available funds: {available_funds}, Required: {required_amount}"
                )
        except Exception:
            logger.warning("Failed to check client funding while attempting to unblock.", exc_info=True)

    def is_in_error_state(self) -> bool:
        return self.blocked

class IllegalStateException(Exception):
    pass
