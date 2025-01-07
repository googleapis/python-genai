export interface ExampleType {
    id: number;
    name: string;
    description?: string;
}

export type ExampleResponse = {
    success: boolean;
    data: ExampleType[];
};

export interface Config {
    apiUrl: string;
    timeout: number;
}