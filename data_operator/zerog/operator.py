from .submission import data_to_segments, create_submission
from .provider import NHProvider
from .spec import TX_PARAMS
import asyncio
from copy import copy


# TODO: convert it to a storage client
class ZeroGStorageClient:
    def __init__(self, url):
        self.provider = NHProvider(url)

    async def upload_file(self, data: bytes):
        segments = data_to_segments(data)
        for segment in segments:
            await self.provider.upload_segment(segment)
        return True


class ContractProxy:
    def __init__(self, contract, blockchain_nodes):
        self.contract = contract
        self.contract_address = contract.address
        self.blockchain_nodes = blockchain_nodes

    def _get_contract(self, node_idx=0):
        return (
            self.contract
            if node_idx == 0
            else self.blockchain_nodes[node_idx].get_contract(self.contract_address)
        )

    def _call(self, fn_name, node_idx, **args):
        assert node_idx < len(self.blockchain_nodes)

        contract = self._get_contract(node_idx)
        return getattr(contract.functions, fn_name)(**args).call()

    def _send(self, fn_name, node_idx, **args):
        assert node_idx < len(self.blockchain_nodes)

        contract = self._get_contract(node_idx)
        return getattr(contract.functions, fn_name)(**args).transact(copy(TX_PARAMS))

    def _logs(self, event_name, node_idx, **args):
        assert node_idx < len(self.blockchain_nodes)

        contract = self._get_contract(node_idx)

        return (
            getattr(contract.events, event_name)
            .create_filter(fromBlock=0, toBlock="latest")
            .get_all_entries()
        )

    def transfer(self, value, node_idx=0):
        tx_params = copy(TX_PARAMS)
        tx_params["value"] = value

        contract = self._get_contract(node_idx)
        contract.receive.transact(tx_params)

    def address(self):
        return self.contract_address


class ZeroGOperator:
    def __init__(self, url):
        self.storage_client = ZeroGStorageClient(url)

    async def register_file(self, task: asyncio.Task):
        file_path = await task
        with open(file_path, "rb") as f:
            data = f.read()

        submissions, data_root = create_submission(data)
        await self.storage_client.upload_file(data)
