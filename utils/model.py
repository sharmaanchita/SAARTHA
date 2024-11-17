class ModelBuilder:
    def __init__(
        self, class_number,on_change = None
    ):
        
        self.on_change = on_change
        self.class_number = class_number
        self.model = self.base_model()
        
        if class_number == 1:
            self.model += self.demand_fulfillment_declaration()
            self.model += self.inventory_carryover_declaration()
            self.model += self.material_balance_declaration()
            self.model += self.class1_objective()
            
        elif class_number == 2:
            self.model += self.demand_fulfillment_declaration()
            self.model += self.inventory_carryover_declaration()
            self.model += self.production_rate_declaration()
            self.model += self.resource_capacity_declaration()
            self.model += self.material_balance_with_transfers_declaration()
            self.model += self.target_stock_declaration()
            self.model += self.storage_capacity_declaration()
            self.model += self.class2_objective()
        else:
            assert False
            
    def _transform(self, declaration):
        return declaration

    def base_model(self):
        return self._transform(
            r"""
            set PRODUCTS;  # Set of products
            set LOCATIONS;  # Set of distribution or production locations
            set PRODUCTS_LOCATIONS within {PRODUCTS, LOCATIONS};  # Restrict table
            set PERIODS ordered;  # Ordered set of time periods for planning
            
            param Demand{p in PRODUCTS, l in LOCATIONS, t in PERIODS} >= 0 default 0;
                # Demand for each product at each location during each time period
            var UnmetDemand{p in PRODUCTS, l in LOCATIONS, t in PERIODS} >= 0;
                # Quantity of demand that is not met for a product at a location in a time period
            var MetDemand{p in PRODUCTS, l in LOCATIONS, t in PERIODS} >= 0;
                # Quantity of demand that is met for a product at a location in a time period

            param InitialInventory{p in PRODUCTS, l in LOCATIONS} >= 0 default 0;
                # Initial inventory levels for each product at each location
            var StartingInventory{p in PRODUCTS, l in LOCATIONS, t in PERIODS} >= 0;
                # Inventory at the beginning of each time period
            var EndingInventory{p in PRODUCTS, l in LOCATIONS, t in PERIODS} >= 0;
                # Inventory at the end of each time period
            var Production{p in PRODUCTS, l in LOCATIONS, t in PERIODS} >= 0;
                # Production volume for each product at each location during each time period
            """
        )
    def demand_fulfillment_declaration(self):
        return self._transform(
            r"""
            s.t. DemandBalance{p in PRODUCTS, l in LOCATIONS, t in PERIODS}:
                Demand[p, l, t] = MetDemand[p, l, t] + UnmetDemand[p, l, t];
                # Ensure that all demand is accounted for either as met or unmet
            """
        )
    
    def inventory_carryover_declaration(self):
        return self._transform(
            r"""
            s.t. InventoryCarryover{p in PRODUCTS, l in LOCATIONS, t in PERIODS}:
                StartingInventory[p, l, t] =
                    if ord(t) > 1 then
                        EndingInventory[p, l, prev(t)]
                    else
                        InitialInventory[p, l];
                # Define how inventory is carried over from one period to the next
            """
        )

    def material_balance_declaration(self):
        return self._transform(
            r"""
            s.t. MaterialBalance{p in PRODUCTS, l in LOCATIONS, t in PERIODS}:
                StartingInventory[p, l, t] + Production[p, l, t] - MetDemand[p, l, t] = EndingInventory[p, l, t];
                # Balance starting inventory and production against demand to determine ending inventory
            """
        )


    def production_rate_declaration(self):
        return self._transform(
            r"""
            set RESOURCES;  # Set of production resources
            
            var ProductionHours{p in PRODUCTS, l in LOCATIONS, r in RESOURCES, t in PERIODS} >= 0; 
                # Production hours for each product, location, resource, and period
            param ProductionRate{p in PRODUCTS, l in LOCATIONS, r in RESOURCES} >= 0 default 0;
                # Production rate for each product at each location and resource (could also depend on the period)
            s.t. ProductionRateConstraint{p in PRODUCTS, l in LOCATIONS, t in PERIODS}:
                Production[p,l,t] == sum{r in RESOURCES} ProductionHours[p,l,r,t] * ProductionRate[p,l,r];
            """
        )

    def resource_capacity_declaration(self):
        return self._transform(
            r"""
            param AvailableCapacity{r in RESOURCES, l in LOCATIONS} >= 0 default 0; 
                # Available capacity for each resource at each location
            s.t. ProductionCapacity{r in RESOURCES, l in LOCATIONS, t in PERIODS}:
                sum{(p, l) in PRODUCTS_LOCATIONS} ProductionHours[p,l,r,t] <= AvailableCapacity[r,l];
            """
        )
    def material_balance_with_transfers_declaration(self):
        return self._transform(
            r"""
            set TRANSFER_LANES within {PRODUCTS, LOCATIONS, LOCATIONS};
                # Valid transfer lanes (From_Location, To_Location)
            var TransfersIN{(p, i, j) in TRANSFER_LANES, t in PERIODS} >= 0;
                # Transfers of product 'p' arriving at location 'j' from location 'i'
            var TransfersOUT{(p, i, j) in TRANSFER_LANES, t in PERIODS} >= 0;
            s.t. MaterialBalanceWithTransfers{p in PRODUCTS, l in LOCATIONS, t in PERIODS}:
                StartingInventory[p,l,t] - MetDemand[p,l,t] + Production[p,l,t]
                + sum{i in LOCATIONS: (p, i, l) in TRANSFER_LANES} TransfersIN[p,i,l,t]
                - sum{j in LOCATIONS: (p, l, j) in TRANSFER_LANES} TransfersOUT[p,l,j,t]
                == EndingInventory[p,l,t];
                # Transfers of product 'p' leaving from location 'i' to location 'j'
            """
        )

    def target_stock_declaration(self):
        return self._transform(
            r"""
            param TargetStock{p in PRODUCTS, l in LOCATIONS} >= 0 default 0;
                # Target stock level for each product and location (could also depend on the period)
            var AboveTarget{p in PRODUCTS, l in LOCATIONS, t in PERIODS} >= 0;
                # Amount above target stock
            var BelowTarget{p in PRODUCTS, l in LOCATIONS, t in PERIODS} >= 0;
            s.t. TargetStockConstraint{p in PRODUCTS, l in LOCATIONS, t in PERIODS}:
                TargetStock[p, l] == EndingInventory[p, l, t] + BelowTarget[p, l, t] - AboveTarget[p, l, t];
                # Amount below target stock
            """
        )

    def storage_capacity_declaration(self):
        return self._transform(
            r"""
            param MaxCapacity{l in LOCATIONS} >= 0;
            subject to StorageCapacityConstraint{l in LOCATIONS, t in PERIODS}:
                sum{(p, l) in PRODUCTS_LOCATIONS} EndingInventory[p, l, t] <= MaxCapacity[l];
                # Maximum storage capacity for each location (could also depend on the period)
            """
        )

    def class1_objective(self):
        return self._transform(
            r"""
            param UnmetDemandPenalty default 10;
                # Penalty cost per unit for unmet demand (impacts decision to meet demand)
            param EndingInventoryPenalty default 5;
                # Penalty cost per unit for ending inventory (reflects carrying cost)

            minimize TotalCost:
                sum {p in PRODUCTS, l in LOCATIONS, t in PERIODS}
                    (UnmetDemandPenalty * UnmetDemand[p, l, t] + EndingInventoryPenalty * EndingInventory[p, l, t]);
                # Objective function to minimize total costs associated with unmet demand and leftover inventory
            """
        )

    def class2_objective(self):
        return self._transform(
            r"""
            param BelowTargetPenalty default 3;
                # Penalty for having inventory below target
            param UnmetDemandPenalty default 10;
                # Penalty cost per unit for unmet demand (impacts decision to meet demand)
            param AboveTargetPenalty default 2;
                # Penalty for having inventory above target
            param EndingInventoryPenalty default 5;
                # Penalty cost per unit for ending inventory (reflects carrying cost)
            param TransferPenalty default 1;
                # Penalty for each unit transferred

            # Minimize total cost objective
            minimize TotalCost:
                sum{p in PRODUCTS, l in LOCATIONS, t in PERIODS} (
                    UnmetDemandPenalty * UnmetDemand[p, l, t] 
                    + EndingInventoryPenalty * EndingInventory[p, l, t] 
                    + AboveTargetPenalty * AboveTarget[p, l, t] 
                    + BelowTargetPenalty * BelowTarget[p, l, t]
                )
                + sum{(p, i, j) in TRANSFER_LANES, t in PERIODS} (
                    TransferPenalty * TransfersOUT[p, i, j, t]
                );
                # Objective: Minimize total cost, which includes penalties for unmet demand, ending inventory, deviations from target stock, and transfers
            """
        )
