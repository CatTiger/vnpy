class TradeProfit:
    __slots__ = ('step', 'total_profit', 'total_loss', 'ratio', 'sample_size')

    def __init__(self, step, total_profit, total_loss, ratio, sample_size):
        self.step = step
        self.total_profit = total_profit
        self.total_loss = total_loss
        self.ratio = ratio
        self.sample_size = sample_size
