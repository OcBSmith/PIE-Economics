using Test
using MacroAIComp

@testset "FiscalPolicy Tests" begin
    @testset "Non-distortionary Ricardian Equivalence" begin
        T = 30
        W = fill(10.0, T)

        # 1. No tax case
        params_no_tax = FiscalPolicyParameters(T, 0.97, 0.02, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 26)
        res_no_tax = solve_non_distortionary(params_no_tax, W)

        # 2. Tax with returned transfers
        params_tax_returned = FiscalPolicyParameters(T, 0.97, 0.02, 0.5, 0.0, 0.40, 0.0, 0.0, 0.0, 26)
        res_tax_returned = solve_non_distortionary(params_tax_returned, W, true)

        @test res_no_tax["C"] ≈ res_tax_returned["C"] atol=1e-6
        @test res_no_tax["B"] ≈ res_tax_returned["B"] atol=1e-6

        # 3. Tax without returned transfers
        res_tax_not_returned = solve_non_distortionary(params_tax_returned, W, false)
        @test all(res_tax_not_returned["C"] .< res_no_tax["C"])
        @test all(abs.(res_tax_not_returned["B"]) .<= abs.(res_no_tax["B"]) .+ 1e-6)
    end

    @testset "Distortionary Equivalence FOC vs Optim" begin
        params = default_calibration(FiscalPolicyParameters)
        W = fill(100.0, params.T)

        for ret_trans in [false, true]
            res_foc = solve_distortionary_foc(params, W, ret_trans)
            res_optim = solve_distortionary_optim(params, W, ret_trans)

            @test res_foc["C"] ≈ res_optim["C"] atol=1e-3
            @test res_foc["L"] ≈ res_optim["L"] atol=1e-3
            @test res_foc["B"] ≈ res_optim["B"] atol=1e-3
        end
    end

    @testset "Labor Supply Distortion" begin
        params_base = FiscalPolicyParameters(30, 0.97, 0.02, 0.5, 0.0, 0.10, 0.0, 0.0, 0.0, 26)
        params_high_tauw = FiscalPolicyParameters(30, 0.97, 0.02, 0.5, 0.0, 0.40, 0.0, 0.0, 0.0, 26)
        params_high_tauc = FiscalPolicyParameters(30, 0.97, 0.02, 0.5, 0.0, 0.10, 0.30, 0.0, 0.0, 26)
        W = fill(100.0, params_base.T)

        res_base = solve_distortionary_optim(params_base, W, true)
        res_tauw = solve_distortionary_optim(params_high_tauw, W, true)
        res_tauc = solve_distortionary_optim(params_high_tauc, W, true)

        mean_l_base = sum(res_base["L"]) / length(res_base["L"])
        mean_l_tauw = sum(res_tauw["L"]) / length(res_tauw["L"])
        mean_l_tauc = sum(res_tauc["L"]) / length(res_tauc["L"])

        @test mean_l_tauw < mean_l_base
        @test mean_l_tauc < mean_l_base
    end

    @testset "Capital Tax Distortion" begin
        params_base = FiscalPolicyParameters(30, 0.97, 0.02, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 26)
        params_high_taur = FiscalPolicyParameters(30, 0.97, 0.02, 0.5, 0.0, 0.0, 0.0, 0.50, 0.0, 26)
        W = fill(100.0, params_base.T)

        res_base = solve_distortionary_optim(params_base, W, false)
        res_taur = solve_distortionary_optim(params_high_taur, W, false)

        mean_b_base = sum(res_base["B"]) / length(res_base["B"])
        mean_b_taur = sum(res_taur["B"]) / length(res_taur["B"])

        @test mean_b_taur < mean_b_base

        slope_base = res_base["C"][end] / res_base["C"][1]
        slope_taur = res_taur["C"][end] / res_taur["C"][1]
        @test slope_taur < slope_base
    end

    @testset "Social Security Substitution" begin
        params_ss = FiscalPolicyParameters(30, 0.97, 0.02, 0.5, 0.0, 0.0, 0.0, 0.0, 0.36, 26)
        W = zeros(params_ss.T)
        W[1:params_ss.t_star] .= 10.0

        res_ss = solve_social_security(params_ss, W)

        params_no_ss = FiscalPolicyParameters(30, 0.97, 0.02, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 26)
        
        Y_equivalent = zeros(params_ss.T)
        for t in 1:params_ss.t_star
            Y_equivalent[t] = 10.0 * (1.0 - params_ss.tau_ss)
        end
        Y_equivalent[params_ss.t_star + 1] = res_ss["Pension"]

        res_no_ss = solve_non_distortionary(params_no_ss, Y_equivalent)

        @test res_ss["C"] ≈ res_no_ss["C"] atol=1e-6
        @test any(b -> b < 0.0, res_ss["B"])
    end
end
