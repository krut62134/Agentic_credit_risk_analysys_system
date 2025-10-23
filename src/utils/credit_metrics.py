def calculate_interest_coverage(ebitda: float, interest_expense: float) -> float:
    """Calculate interest coverage ratio"""
    if interest_expense == 0:
        return float('inf')
    return ebitda / interest_expense

def calculate_altman_z_score(working_capital: float, retained_earnings: float, 
                             ebit: float, market_cap: float, sales: float, 
                             total_assets: float, total_liabilities: float) -> dict:
    """Calculate Altman Z-Score for bankruptcy prediction"""
    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets  
    x3 = ebit / total_assets
    x4 = market_cap / total_liabilities
    x5 = sales / total_assets
    
    z_score = 1.2*x1 + 1.4*x2 + 3.3*x3 + 0.6*x4 + 1.0*x5
    
    if z_score > 2.99:
        zone = "Safe"
    elif z_score > 1.81:
        zone = "Grey"
    else:
        zone = "Distress"
    
    return {"z_score": round(z_score, 2), "zone": zone}

def assess_credit_rating(debt_to_equity: float, debt_to_assets: float, 
                        interest_coverage: float) -> dict:
    """Moody's-style credit rating assessment"""
    
    # Investment grade thresholds
    if debt_to_equity < 0.3 and interest_coverage > 8:
        rating = "Aaa"
        risk = "Minimal"
    elif debt_to_equity < 0.5 and interest_coverage > 6:
        rating = "Aa"
        risk = "Very Low"
    elif debt_to_equity < 1.0 and interest_coverage > 4:
        rating = "A"
        risk = "Low"
    elif debt_to_equity < 1.5 and interest_coverage > 2.5:
        rating = "Baa"
        risk = "Moderate"
    # Speculative grade
    elif debt_to_equity < 2.0 and interest_coverage > 1.5:
        rating = "Ba"
        risk = "Substantial"
    else:
        rating = "B"
        risk = "High"
    
    return {
        "rating": rating,
        "risk_level": risk,
        "investment_grade": rating in ["Aaa", "Aa", "A", "Baa"]
    }
