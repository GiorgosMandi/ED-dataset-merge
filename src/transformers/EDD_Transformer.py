from .Transformer import Transformer
from tqdm import tqdm
from ..utils import utilities


class EDDTransformer(Transformer):

    def __init__(self, edd_path, stanford_core_path):
        super().__init__(stanford_core_path)
        print("edd-transformer initialization")
        self.id_base = "EDD-instance-"
        self.path = edd_path
        self.origin = "EDD"
