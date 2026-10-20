class AllocationValidator:
    def __init__(self, cfg: dict):
        self.cfg = cfg or {}

    def validate(self):
        errs = []
        if not self.cfg.get("version"): errs.append("missing 'version'")
        if not self.cfg.get("portfolio"): errs.append("missing 'portfolio'")
        lp = self.cfg.get("live_params") or {}
        if "max_positions" not in lp: errs.append("missing live_params.max_positions")
        if "max_per_position_pct" not in lp: errs.append("missing live_params.max_per_position_pct")
        return (len(errs) == 0, errs)
