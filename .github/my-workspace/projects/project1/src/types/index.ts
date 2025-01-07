export interface ExampleType {
    id: number;
    name: string;
    description?: string;
}

export type ExampleResponse = {
    success: boolean;
    data: ExampleType[];
};