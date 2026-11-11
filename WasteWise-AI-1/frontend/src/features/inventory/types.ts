export interface InventoryItem {
    id: string;
    name: string;
    quantity: number;
    unit: string;
    location: string;
    expirationDate: Date;
    supplier: string;
    category: string;
}

export interface InventoryState {
    items: InventoryItem[];
    loading: boolean;
    error: string | null;
}

export type AddInventoryItemPayload = Omit<InventoryItem, 'id'>;

export type UpdateInventoryItemPayload = InventoryItem;

export type DeleteInventoryItemPayload = string; // id of the item to delete

export interface FetchInventoryResponse {
    items: InventoryItem[];
    totalCount: number;
}