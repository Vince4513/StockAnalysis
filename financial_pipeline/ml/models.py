# Basic libraries
import numpy as np
import pandas as pd
from typing import List
from sklearn.model_selection import train_test_split

# Pipeline libraries
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Imputation libraries
from sklearn.impute import SimpleImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

# Categorical libraries
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import OneHotEncoder

# Model libraries
# from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor

# Metrics libraries
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import cross_val_score

# ==================================================================================================================================================
# Models Class
# ==================================================================================================================================================

class Models:
    """Models class here to do machine learning predictions"""

    def __init__(self, df: pd.DataFrame, target: str):
        # Remove rows with missing target
        df.dropna(axis=0, subset=[target], inplace=True)
        
        # Separate target from predictors
        self.y = df[target] # <---- possible problem de type
        self.X_full = df.drop([target], axis=1)
    # End def __init__

    def _preprocess_df(self) -> tuple:
        """Determine the numeric, low and high columns to learn properly after

        Returns:
            tuple: columns low categorical, high categorical, num 
        """
        # "Cardinality" means the number of unique values in a column
        # Select categorical columns with relatively low cardinality (convenient but arbitrary)
        low_categorical_cols = [cname for cname in self.X_full.columns if
                            self.X_full[cname].nunique() < 10 and 
                            self.X_full[cname].dtype == "object"]

        high_categorical_cols = [cname for cname in self.X_full.columns if 
                            self.X_full[cname].nunique() >= 10 and 
                            self.X_full[cname].dtype == "object"]

        # Select numerical columns
        numerical_cols = [cname for cname in self.X_full.columns if 
                        self.X_full[cname].dtype in ['int64', 'float64']]

        df_cols = pd.DataFrame.from_dict({
            'Numerical':numerical_cols, 
            'L_Categorical':low_categorical_cols,
            'H_Categorical':high_categorical_cols}, 
            orient='index').T
        
        print(f'Preprocess: {df_cols}')
        
        return low_categorical_cols, high_categorical_cols, numerical_cols
    # End def _preprocess_df

    def _pipeline_construction(self, n_estimators: int) -> Pipeline:
        """Construct the pipeline combining the preprocessor and the model

        Args:
            n_estimators (int): Number of trees in the model

        Returns:
            Pipeline: All the steps to apply on the X_full before training the dataset
        """
        
        # Retrieve the types of columns 
        numerical_cols, low_categorical_cols, high_categorical_cols = self._preprocess_df()

        # Preprocessing for numerical data
        numerical_transformer = IterativeImputer(max_iter=10, random_state=0)

        # Preprocessing for low categorical data
        l_categorical_transformer = Pipeline(steps=[
            ('it_imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])

        # Preprocessing for high categorical data
        h_categorical_transformer = Pipeline(steps=[
            ('it_imputer', SimpleImputer(strategy='most_frequent')),
            ('ordinal', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=70))
        ])

        # Bundle preprocessing for numerical and categorical data
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, numerical_cols),
                ('lcat', l_categorical_transformer, low_categorical_cols),
                ('hcat', h_categorical_transformer, high_categorical_cols)
            ])
        
        # Define model
        # model = XGBRegressor(
        #     n_estimators=n_estimators, 
        #     learning_rate=0.05, 
        #     #early_stopping_rounds = 5,
        #     #eval_set = [(X, y)],
        #     #verbose=False,
        #     random_state=0
        # )
        model = RandomForestRegressor(
           n_estimators=n_estimators, 
           max_depth=20,
           min_samples_split=4,
           min_samples_leaf=2,
           n_jobs= -1,
           random_state=0
        ) 
        
        # Bundle preprocessing and modeling code in a pipeline
        pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                    ('model', model)
                                    ])
        return pipeline
    # End def _pipeline_construction

    def get_score(self, estimators: int) -> List:
        """Return the average MAE over 5 CV folds of XGBoost model.

        Args:
            estimators (int): the number of trees in the forest

        Returns:
            List: _description_
        """
        
        # Pipeline construction 
        my_pipeline = self._pipeline_construction(estimators)
        X = self.X_full
        y = self.y

        # Perform manual cross-validation with early stopping
        scores = []
        for train_index, val_index in KFold(n_splits=5, shuffle=True, random_state=0).split(X):
            X_train, X_val = X.iloc[train_index], X.iloc[val_index]
            y_train, y_val = y.iloc[train_index], y.iloc[val_index]
            
            # Fit the model
            my_pipeline.fit(X_train, y_train)
            
            # Evaluate on the validation set
            val_pred = my_pipeline.predict(X_val)
            score = mean_absolute_error(y_val, val_pred)
            scores.append(score)
        
        return [my_pipeline, np.mean(scores)]
    # End def get_score

    def plot_errors(self) -> None:
        n_estimators = list(range(100, 501, 100))
        results = { 
            estimator: {
                'pipe': self.get_score(estimator, self.X_full, self.y)[0],
                'mae': self.get_score(estimator, self.X_full, self.y)[1]}
            for estimator in n_estimators
        }

        import matplotlib.pyplot as plt

        mae_values = [result['mae'] for result in results.values()]
        # Plot
        plt.plot(n_estimators, mae_values)
        plt.xlabel('Number of Estimators')
        plt.ylabel('Mean Absolute Error')
        plt.title('Mean Absolute Error vs. Number of Estimators')
        plt.grid(True)
        plt.show()
    # End def plot_errors
# End class Models